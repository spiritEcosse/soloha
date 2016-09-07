from oscar.apps.basket.abstract_models import *  # noqa
from django.utils.translation import ugettext_lazy as _


class Line(AbstractLine):
    def attributes_feature(self):
        return [attribute.feature for attribute in self.attributes.all()]


class Basket(AbstractBasket):
    def all_lines(self):
        """
        Return a cached set of basket lines.

        This is important for offers as they alter the line models and you
        don't want to reload them from the DB as that information would be
        lost.
        """
        if self.id is None:
            return self.lines.none()
        if self._lines is None:
            self._lines = (
                self.lines
                    .select_related('product', 'product__product_class', 'stockrecord')
                    .prefetch_related('attributes', 'product__images', 'product__categories__parent__parent',
                                      'product__stockrecords'))
        return self._lines

    def add_product(self, product, quantity=1, options=None, version=None):
        """
        Add a product to the basket

        'stock_info' is the price and availability data returned from
        a partner strategy class.

        The 'options' list should contains dicts with keys 'option' and 'value'
        which link the relevant product.Option model and string value
        respectively.

        Returns (line, created).
          line: the matching basket line
          created: whether the line was created or updated

        """
        if options is None:
            options = []
        if not self.id:
            self.save()

        # Ensure that all lines are the same currency
        price_currency = self.currency

        # print version.stockrecord.price_excl_tax
        stock_info = self.strategy.fetch_for_product(product, stockrecord=version.stockrecord)

        if price_currency and stock_info.price.currency != price_currency:
            raise ValueError((
                                 "Basket lines must all have the same currency. Proposed "
                                 "line has currency %s, while basket has currency %s")
                             % (stock_info.price.currency, price_currency))

        if stock_info.stockrecord is None:
            raise ValueError((
                                 "Basket lines must all have stock records. Strategy hasn't "
                                 "found any stock record for product %s") % product)

        # Line reference is used to distinguish between variations of the same
        # product (eg T-shirts with different personalisations)
        line_ref = self._create_line_reference(
            product, stock_info.stockrecord, options, version.attributes.all())

        # Determine price to store (if one exists).  It is only stored for
        # audit and sometimes caching.
        defaults = {
            'quantity': quantity,
            'price_excl_tax': stock_info.price.excl_tax,
            'price_currency': stock_info.price.currency,
        }
        if stock_info.price.is_tax_known:
            defaults['price_incl_tax'] = stock_info.price.incl_tax

        line, created = self.lines.get_or_create(
            line_reference=line_ref,
            product=product,
            stockrecord=stock_info.stockrecord,
            defaults=defaults)

        if created:
            # for option_dict in options:
            #     line.attributes.create(option=option_dict['option'], value=option_dict['value'])

            for attribute in version.attributes.all():
                line.attributes.create(feature=attribute)
        else:
            line.quantity += quantity
            line.save()
        self.reset_offer_applications()

        # Returning the line is useful when overriding this method.
        return line, created
    add_product.alters_data = True
    add = add_product

    def _create_line_reference(self, product, stockrecord, options, attributes=None):
        """
        Returns a reference string for a line based on the item
        and its options.
        """
        base = '%s_%s' % (product.id, stockrecord.id)

        if options:
            base = "%s_%s" % (base, zlib.crc32(repr(options).encode('utf8')))

        if attributes is not None:
            base = "%s_%s" % (base, zlib.crc32(repr(attributes).encode('utf8')))

        return base


from oscar.apps.basket.models import *  # noqa

feature = models.ForeignKey('catalogue.Feature', verbose_name=_('Feature'), null=True, blank=True)
feature.contribute_to_class(LineAttribute, "feature")

option = LineAttribute._meta.get_field('option')
option.null = True
option.blank = True
LineAttribute._meta.get_field('value').blank = True
