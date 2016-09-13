from oscar.apps.basket.abstract_models import *  # noqa
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from oscar.core.loading import get_model
from django.db.models.query import Prefetch
from apps.catalogue.fiters import Filter
ProductFeature = get_model('catalogue', 'ProductFeature')


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

    def add_product(self, product, quantity=1, options=None, version=None, product_images=None):
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
            attributes = line.stockrecord.product_version.attributes.prefetch_related(
                *self.prefetch(product, product_images)
            )

            for attribute in attributes:
                line_attributes = line.attributes.create(feature=attribute)

                if attribute.have_product_images:
                    line_attributes.product_images.add(product_images)
        else:
            line_attributes = line.attributes.select_related('feature').prefetch_related(
                *self.prefetch(product, product_images, feature=True)
            )

            for line_attribute in line_attributes:
                if line_attribute.feature.have_product_images:
                    line_attribute.product_images.clear()
                    line_attribute.product_images.add(product_images)

            line.quantity += quantity
            line.save()
        self.reset_offer_applications()

        # Returning the line is useful when overriding this method.
        return line, created
    add_product.alters_data = True
    add = add_product

    def prefetch(self, product, product_images, feature=False):
        lookup = Filter(product=product)
        prefetch = []
        fields = 'feature__' if feature else ''
        fields += 'product_features'

        prefetch.append(
            Prefetch(
                fields,
                queryset=ProductFeature.objects.filter(
                    **lookup.filter_feature_parent(
                        {
                            'product_with_images': product_images.product
                        }
                    )
                ),
                to_attr='have_product_images',
            )
        )

        return prefetch

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

product_images = models.ManyToManyField(
    'catalogue.ProductImage', blank=True, related_name='line_attributes', verbose_name=_('Product images')
)
product_images.contribute_to_class(LineAttribute, "product_images")

option = LineAttribute._meta.get_field('option')
option.null = True
option.blank = True
LineAttribute._meta.get_field('value').blank = True
