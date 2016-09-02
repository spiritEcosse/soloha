from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.html import strip_entities
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import IMAGE_NOT_FOUND, MEDIA_ROOT
from easy_thumbnails.exceptions import (
    InvalidImageFormatError, EasyThumbnailsError)
from mptt.models import MPTTModel, TreeForeignKey
from oscar.apps.catalogue.abstract_models import *  # noqa
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from filer.fields.image import FilerImageField
import logging
from django.template import loader, Context

logger = logging.getLogger(__name__)

REGEXP_PHONE = r'/^((8|\+38)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/'
REGEXP_EMAIL = r'/^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$/'

BrowsableProductManagerCore = get_class('catalogue.managers', 'BrowsableProductManager')


def check_exist_image(image):
    current_path = os.getcwd()
    os.chdir(MEDIA_ROOT)
    image_not_found = True

    if not os.path.exists(os.path.abspath(image)) or not os.path.isfile(os.path.abspath(image)):
        image = IMAGE_NOT_FOUND
        image_not_found = False

        if not os.path.exists(os.path.abspath(image)):
            logger.error('image - {} not found!'.format(os.path.abspath(image)))

    os.chdir(current_path)
    return image, image_not_found


class CommonFeatureProduct(object):
    product = None

    def product_enable(self):
        return self.product.enable
    product_enable.short_description = _('Enable product')

    def product_categories_to_str(self):
        return self.product.categories_to_str()
    product_categories_to_str.short_description = _("Categories")

    def product_partners_to_str(self):
        return self.product.partners_to_str()
    product_partners_to_str.short_description = _("Partners")

    def thumb(self):
        return self.product.thumb()
    thumb.allow_tags = True
    thumb.short_description = _('Image of product')

    def product_date_updated(self):
        return self.product.date_updated
    product_date_updated.short_description = _("Product date updated")


class EnableManagerProduct(models.Manager):
    def get_queryset(self):
        return self.get_queryset().filter(enable=True)


@python_2_unicode_compatible
class AbstractProduct(models.Model):
    # Title is mandatory for canonical products but optional for child products
    title = models.CharField(pgettext_lazy(u'Product title', u'Title'), max_length=300)
    slug = models.SlugField(_('Slug'), max_length=400, unique=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=520)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    description = RichTextUploadingField(_('Description'), blank=True)
    views_count = models.IntegerField(verbose_name='views count', editable=False, default=0)

    STANDALONE, PARENT, CHILD = 'standalone', 'parent', 'child'
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    structure = models.CharField(
        _("Product structure"), max_length=10, choices=STRUCTURE_CHOICES,
        default=STANDALONE)

    upc = NullCharField(
        _("UPC"), max_length=64, blank=True, null=True, unique=True,
        help_text=_("Universal Product Code (UPC) is an identifier for "
                    "a product which is not specific to a particular "
                    " supplier. Eg an ISBN for a book."))

    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=_("Parent product"),
        help_text=_("Only choose a parent product if you're creating a child "
                    "product.  For example if this is a size "
                    "4 of a particular t-shirt.  Leave blank if this is a "
                    "stand-alone product (i.e. there is only one version of"
                    " this product)."))

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    # This field is used by Haystack to reindex search
    date_updated = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True)

    categories = models.ManyToManyField('catalogue.Category', related_name="products", verbose_name=_("Categories"))
    filters = models.ManyToManyField('catalogue.Feature', related_name="filter_products", verbose_name=_('Filters of product'), blank=True)
    attributes = models.ManyToManyField('catalogue.Feature', through='ProductFeature', verbose_name=_('Attribute of product'), related_name="attr_products", blank=True)
    characteristics = models.ManyToManyField('catalogue.Feature', verbose_name='Characteristics', related_name='characteristic_products', blank=True)
    options = models.ManyToManyField('catalogue.Feature', through='ProductOptions', related_name='option_products', verbose_name='Additional options')

    non_standard_price_retail = models.DecimalField(_("Non-standard retail price"), decimal_places=2, max_digits=12, blank=True, default=0)
    non_standard_cost_price = models.DecimalField(_("Non-standard cost price"), decimal_places=2, max_digits=12, blank=True, default=0)

    #: "Kind" of product, e.g. T-Shirt, Book, etc.
    #: None for child products, they inherit their parent's product class
    product_class = models.ForeignKey(
        'catalogue.ProductClass', on_delete=models.PROTECT,
        verbose_name=_('Product type'), related_name="products",
        help_text=_("Choose what type of product this is"))
    recommended_products = models.ManyToManyField(
        'catalogue.Product', through='catalogue.ProductRecommendation', blank=True,
        verbose_name=_("Recommended products"),
        help_text=_("These are products that are recommended to accompany the "
                    "main product."))

    # Denormalised product rating - used by reviews app.
    # Product has no ratings if rating is None
    rating = models.FloatField(_('Rating'), null=True, editable=False)

    #: Determines if a product may be used in an offer. It is illegal to
    #: discount some types of product (e.g. ebooks) and this field helps
    #: merchants from avoiding discounting such products
    #: Note that this flag is ignored for child products; they inherit from
    #: the parent product.
    is_discountable = models.BooleanField(
        _("Is discountable?"), default=True, help_text=_(
            "This flag indicates if this product can be used in an offer "
            "or not"))

    objects = ProductManager()
    objects_enable = EnableManagerProduct()
    browsable = BrowsableProductManager()
    separator = ','

    class Meta:
        abstract = True
        app_label = 'catalogue'
        ordering = ('-date_updated', '-views_count', 'title', )
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def __str__(self):
        if self.title:
            return self.title
        if self.attribute_summary:
            return u"%s (%s)" % (self.get_title(), self.attribute_summary)
        else:
            return self.get_title()

    def get_absolute_url(self):
        """
        Return a product's absolute url
        """
        dict_values = {'product_slug': self.slug}

        if self.categories.exists():
            dict_values.update({'category_slug': self.categories.first().full_slug})

        return reverse('catalogue:detail', kwargs=dict_values)

    def images_all(self):
        images = []

        for image in self.images.all():
            exist_image = False

            if image.original is not None:
                image, exist_image = check_exist_image(image.original.file.name)

            if exist_image:
                images.append(image)

        if not images:
            images.append(self.primary_image())

        return images

    def thumb(self, original=None):
        if original is not None:
            image = original
        else:
            image = self.primary_image()

        image, exist_image = check_exist_image(image)
        return loader.get_template('admin/catalogue/product/thumb.html').render(Context({'image': image}))
    thumb.allow_tags = True
    thumb.short_description = _('Image')

    def categories_to_str(self):
        return self.separator.join([category.name for category in self.get_categories().all()])
    categories_to_str.short_description = _("Categories")

    def partners_to_str(self):
        return self.separator.join([stock.partner.name for stock in self.stockrecords.all()])
    categories_to_str.short_description = _("Partners")

    def clean(self):
        """
        Validate a product. Those are the rules:

        +---------------+-------------+--------------+--------------+
        |               | stand alone | parent       | child        |
        +---------------+-------------+--------------+--------------+
        | title         | required    | required     | optional     |
        +---------------+-------------+--------------+--------------+
        | product class | required    | required     | must be None |
        +---------------+-------------+--------------+--------------+
        | parent        | forbidden   | forbidden    | required     |
        +---------------+-------------+--------------+--------------+
        | stockrecords  | 0 or more   | forbidden    | 0 or more    |
        +---------------+-------------+--------------+--------------+
        | categories    | 1 or more   | 1 or more    | forbidden    |
        +---------------+-------------+--------------+--------------+
        | attributes    | optional    | optional     | optional     |
        +---------------+-------------+--------------+--------------+
        | rec. products | optional    | optional     | unsupported  |
        +---------------+-------------+--------------+--------------+
        | options       | optional    | optional     | forbidden    |
        +---------------+-------------+--------------+--------------+

        Because the validation logic is quite complex, validation is delegated
        to the sub method appropriate for the product's structure.
        """
        getattr(self, '_clean_%s' % self.structure)()
        # if not self.is_parent:
        #     self.attr.validate_attributes()

    def _clean_standalone(self):
        """
        Validates a stand-alone product
        """
        if not self.title:
            raise ValidationError(_("Your product must have a title."))
        if not self.product_class:
            raise ValidationError(_("Your product must have a product class."))
        if self.parent_id:
            raise ValidationError(_("Only child products can have a parent."))

    def _clean_child(self):
        """
        Validates a child product
        """
        if not self.parent_id:
            raise ValidationError(_("A child product needs a parent."))
        if self.parent_id and not self.parent.is_parent:
            raise ValidationError(
                _("You can only assign child products to parent products."))
        if self.product_class:
            raise ValidationError(
                _("A child product can't have a product class."))
        if self.pk and self.categories.exists():
            raise ValidationError(
                _("A child product can't have a category assigned."))
        # Note that we only forbid options on product level
        if self.pk and self.product_options.exists():
            raise ValidationError(
                _("A child product can't have options."))

    def _clean_parent(self):
        """
        Validates a parent product.
        """
        self._clean_standalone()
        if self.has_stockrecords:
            raise ValidationError(
                _("A parent product can't have stockrecords."))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_title())
        super(AbstractProduct, self).save(*args, **kwargs)
        # self.attr.save()

    # Properties

    @property
    def is_standalone(self):
        return self.structure == self.STANDALONE

    @property
    def is_parent(self):
        return self.structure == self.PARENT

    @property
    def is_child(self):
        return self.structure == self.CHILD

    def can_be_parent(self, give_reason=False):
        """
        Helps decide if a the product can be turned into a parent product.
        """
        reason = None
        if self.is_child:
            reason = _('The specified parent product is a child product.')
        if self.has_stockrecords:
            reason = _(
                "One can't add a child product to a product with stock"
                " records.")
        is_valid = reason is None
        if give_reason:
            return is_valid, reason
        else:
            return is_valid

    # @property
    # def options(self):
    #     """
    #     Returns a set of all valid options for this product.
    #     It's possible to have options product class-wide, and per product.
    #     """
    #     return self.options.all()

    @property
    def is_shipping_required(self):
        return self.get_product_class().requires_shipping

    @property
    def has_stockrecords(self):
        """
        Test if this product has any stockrecords
        """
        return self.stockrecords.exists()

    @property
    def num_stockrecords(self):
        return self.stockrecords.count()

    @property
    def attribute_summary(self):
        """
        Return a string of all of a product's attributes
        """
        attributes = self.attribute_values.all()
        pairs = [attribute.summary() for attribute in attributes]
        return ", ".join(pairs)

    # The two properties below are deprecated because determining minimum
    # price is not as trivial as it sounds considering multiple stockrecords,
    # currencies, tax, etc.
    # The current implementation is very naive and only works for a limited
    # set of use cases.
    # At the very least, we should pass in the request and
    # user. Hence, it's best done as an extension to a Strategy class.
    # Once that is accomplished, these properties should be removed.

    @property
    @deprecated
    def min_child_price_incl_tax(self):
        """
        Return minimum child product price including tax.
        """
        return self._min_child_price('incl_tax')

    @property
    @deprecated
    def min_child_price_excl_tax(self):
        """
        Return minimum child product price excluding tax.

        This is a very naive approach; see the deprecation notice above. And
        only use it for display purposes (e.g. "new Oscar shirt, prices
        starting from $9.50").
        """
        return self._min_child_price('excl_tax')

    def _min_child_price(self, prop):
        """
        Return minimum child product price.

        This is for visual purposes only. It ignores currencies, most of the
        Strategy logic for selecting stockrecords, knows nothing about the
        current user or request, etc. It's only here to ensure
        backwards-compatibility; the previous implementation wasn't any
        better.
        """
        strategy = Selector().strategy()

        children_stock = strategy.select_children_stockrecords(self)
        prices = [
            strategy.pricing_policy(child, stockrecord)
            for child, stockrecord in children_stock]
        raw_prices = sorted([getattr(price, prop) for price in prices])
        return raw_prices[0] if raw_prices else None

    # Wrappers for child products

    def get_title(self):
        """
        Return a product's title or it's parent's title if it has no title
        """
        title = self.title
        if not title and self.parent_id:
            title = self.parent.title
        return title
    get_title.short_description = pgettext_lazy(u"Product title", u"Title")

    def get_product_class(self):
        """
        Return a product's item class. Child products inherit their parent's.
        """
        if self.is_child:
            return self.parent.product_class
        else:
            return self.product_class
    get_product_class.short_description = _("Product class")

    def get_is_discountable(self):
        """
        At the moment, is_discountable can't be set individually for child
        products; they inherit it from their parent.
        """
        if self.is_child:
            return self.parent.is_discountable
        else:
            return self.is_discountable

    def get_categories(self):
        """
        Return a product's categories or parent's if there is a parent product.
        """
        if self.is_child:
            return self.parent.categories
        else:
            return self.categories
    get_categories.short_description = _("Categories")

    # Images

    def get_missing_image(self):
        """
        Returns a missing image object.
        """
        # This class should have a 'name' property so it mimics the Django file
        # field.
        return MissingProductImage()

    def primary_image(self):
        """
        Returns the primary image for a product. Usually used when one can
        only display one product image, e.g. in a list of products.
        """
        image = self.get_missing_image().name

        if self.images.exists():
            original = self.images.all()[0].original

            if original is not None:
                image = original.file.name

        image, exist_image = check_exist_image(image)
        return image

    # Updating methods

    def update_rating(self):
        """
        Recalculate rating field
        """
        self.rating = self.calculate_rating()
        self.save()
    update_rating.alters_data = True

    def calculate_rating(self):
        """
        Calculate rating value
        """
        result = self.reviews.filter(
            status=self.reviews.model.APPROVED
        ).aggregate(
            sum=Sum('score'), count=Count('id'))
        reviews_sum = result['sum'] or 0
        reviews_count = result['count'] or 0
        rating = None
        if reviews_count > 0:
            rating = float(reviews_sum) / reviews_count
        return rating

    def has_review_by(self, user):
        if user.is_anonymous():
            return False
        return self.reviews.filter(user=user).exists()

    def is_review_permitted(self, user):
        """
        Determines whether a user may add a review on this product.

        Default implementation respects OSCAR_ALLOW_ANON_REVIEWS and only
        allows leaving one review per user and product.

        Override this if you want to alter the default behaviour; e.g. enforce
        that a user purchased the product to be allowed to leave a review.
        """
        if user.is_authenticated() or settings.OSCAR_ALLOW_ANON_REVIEWS:
            return not self.has_review_by(user)
        else:
            return False

    @cached_property
    def num_approved_reviews(self):
        return self.reviews.filter(
            status=self.reviews.model.APPROVED).count()

    def get_data(self, names_fields):
        """
        get values by name field
        :param names_fields: name fields in this object
        :return: dict
        Example
            {'pk': 1, title: 'Product'}
        """
        data = {}
        for name_field in names_fields:
            data[name_field] = getattr(self, name_field)
        return data

    def get_values(self):
        values = dict()
        values['title'] = strip_entities(self.title)
        values['absolute_url'] = self.get_absolute_url()

        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(self)
        if info.availability.is_available_to_buy:
            values['price'] = str(info.stockrecord.price_excl_tax)
        else:
            values['price'] = str(info.availability.message)

        options = {'size': (220, 165), 'crop': True}

        image = getattr(self.primary_image(), 'original', IMAGE_NOT_FOUND)

        try:
            values['image'] = get_thumbnailer(image).get_thumbnail(options).url
        except InvalidImageFormatError:
            values['image'] = get_thumbnailer(IMAGE_NOT_FOUND).get_thumbnail(options).url
        return values


@python_2_unicode_compatible
class AbstractFeature(MPTTModel):
    title = models.CharField(max_length=255)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=255, unique=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    sort = models.IntegerField(blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True)
    bottom_line = models.IntegerField(verbose_name=_('Bottom line size'), blank=True, null=True)
    top_line = models.IntegerField(verbose_name=_('Top line size'), blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ('sort', 'title', )

    class Meta:
        abstract = True
        unique_together = ('slug', 'parent', )
        ordering = ('sort', 'title', )
        verbose_name = _('Feature')
        verbose_name_plural = _('Features')

    def __str__(self):
        if self.parent:
            return u'{} > {}'.format(self.parent, self.title)
        return self.title

    def save(self, *args, **kwargs):
        if not self.sort:
            self.sort = 0

        if not self.slug and self.title:
            self.slug = ''

            if self.parent:
                self.slug = self.parent.slug + '-'
            self.slug += slugify(self.title)

        super(AbstractFeature, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug

    def get_values(self, names_fields):
        """
        get values by name field
        :param names_fields: name fields in this object
        :return: dict
        Example
            {'pk': 1, title: 'Feature'}
        """
        data = {}
        for name_field in names_fields:
            data[name_field] = getattr(self, name_field)
        return data


@python_2_unicode_compatible
class AbstractProductImage(models.Model, CommonFeatureProduct):
    """
    An image of a product
    """
    product = models.ForeignKey('catalogue.Product', related_name='images', verbose_name=_("Product"))
    original = FilerImageField(verbose_name=_("Original"), null=True, blank=True, related_name="original")
    caption = models.CharField(_("Caption"), max_length=200, blank=True)

    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(_("Display order"), default=0,
        help_text=_("An image with a display order of zero will be the primary image for a product"))
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)

    class Meta:
        abstract = True
        app_label = 'catalogue'
        # Any custom models should ensure that this ordering is unchanged, or
        # your query count will explode. See AbstractProduct.primary_image.
        ordering = ("product", "display_order", )
        unique_together = ("product", "display_order")
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')

    def __str__(self):
        return u"Image of '%s'" % getattr(self, 'product', None)

    def is_primary(self):
        """
        Return bool if image display order is 0
        """
        return self.display_order == 0

    def thumb(self):
        image = self.original.file.name if self.original is not None else IMAGE_NOT_FOUND
        image, exist_image = check_exist_image(image)
        return loader.get_template('admin/catalogue/product/thumb.html').render(Context({'image': image}))
    thumb.allow_tags = True
    thumb.short_description = _('Image')

    def delete(self, *args, **kwargs):
        """
        Always keep the display_order as consecutive integers. This avoids
        issue #855.
        """

        images = self.product.images.all().exclude(pk=self.pk)

        super(AbstractProductImage, self).delete(*args, **kwargs)

        for idx, image in enumerate(images):
            image.display_order = idx
            image.save()


@python_2_unicode_compatible
class CustomAbstractCategory(MPTTModel):
    name = models.CharField(_('Name'), max_length=300, db_index=True)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=400, unique=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True, db_index=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=480)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    sort = models.IntegerField(blank=True, null=True, default=0, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    link_banner = models.URLField(_('Link banner'), blank=True, null=True, max_length=555)
    description = RichTextUploadingField(_('Description'), blank=True)
    image_banner = FilerImageField(verbose_name=_('Image banner'), blank=True, null=True,
                                   related_name='category_image_banner')
    icon = FilerImageField(verbose_name=_('Icon'), blank=True, null=True, related_name='category_icon')
    image = FilerImageField(verbose_name=_('Image'), null=True, blank=True, related_name="category_image")
    _slug_separator = '/'
    _full_name_separator = ' > '

    class MPTTMeta:
        order_insertion_by = ('sort', 'name', )

    class Meta:
        abstract = True
        ordering = ('sort', 'name', )
        #Todo add index_together like this
        # index_together = (('name', 'slug', ), ('enable', 'created', 'sort', ), )
        unique_together = ('slug', 'parent')
        app_label = 'catalogue'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """
        Returns a string representation of the category and it's ancestors,
        e.g. 'Books > Non-fiction > Essential programming'.

        It's rarely used in Oscar's codebase, but used to be stored as a
        CharField and is hence kept for backwards compatibility. It's also
        sufficiently useful to keep around.
        """
        #Todo category.name to str
        names = [unicode(category.name) for category in self.get_ancestors_and_self()]
        return self._full_name_separator.join(names)

    @property
    def full_slug(self):
        """
        Returns a string of this category's slug concatenated with the slugs
        of it's ancestors, e.g. 'books/non-fiction/essential-programming'.

        Oscar used to store this as in the 'slug' model field, but this field
        has been re-purposed to only store this category's slug and to not
        include it's ancestors' slugs.
        """
        slugs = [category.slug for category in self.get_ancestors_through_parent(include_self=True)]
        return self._slug_separator.join(map(str, slugs))

    def get_ancestors_through_parent(self, include_self=True):
        """
        Get ancestors through the field of the parent.
        :param include_self:
            by default True
            points include the current object in the category list
        :return:
            list of parents
        """
        parents = list()
        parents = self.get_parents(obj=self, parents=parents)

        if include_self is True:
            parents += [self]
        return parents

    def get_parents(self, obj, parents):
        if obj.parent:
            parents.append(obj.parent)
            return self.get_parents(obj=obj.parent, parents=parents)
        parents.reverse()
        return parents

    def generate_slug(self):
        """
        Generates a slug for a category. This makes no attempt at generating
        a unique slug.
        """
        return slugify(self.name)

    def ensure_slug_uniqueness(self):
        """
        Ensures that the category's slug is unique amongst it's siblings.
        This is inefficient and probably not thread-safe.
        """
        unique_slug = self.slug
        siblings = self.get_siblings().exclude(pk=self.pk)
        next_num = 2
        while siblings.filter(slug=unique_slug).exists():
            unique_slug = '{slug}_{end}'.format(slug=self.slug, end=next_num)
            next_num += 1

        if unique_slug != self.slug:
            self.slug = unique_slug
            self.save()

    def save(self, *args, **kwargs):
        """
        Oscar traditionally auto-generated slugs from names. As that is
        often convenient, we still do so if a slug is not supplied through
        other means. If you want to control slug creation, just create
        instances with a slug already set, or expose a field on the
        appropriate forms.
        """
        if self.slug:
            # Slug was supplied. Hands off!
            super(CustomAbstractCategory, self).save(*args, **kwargs)
        else:
            self.slug = self.generate_slug()
            super(CustomAbstractCategory, self).save(*args, **kwargs)
            # We auto-generated a slug, so we need to make sure that it's
            # unique. As we need to be able to inspect the category's siblings
            # for that, we need to wait until the instance is saved. We
            # update the slug and save again if necessary.
            self.ensure_slug_uniqueness()

    def get_ancestors_and_self(self):
        """
        Gets ancestors and includes itself. Use treebeard's get_ancestors
        if you don't want to include the category itself. It's a separate
        function as it's commonly used in templates.
        """
        return list(self.get_ancestors()) + [self]

    def get_descendants_and_self(self):
        """
        Gets descendants and includes itself. Use treebeard's get_descendants
        if you don't want to include the category itself. It's a separate
        function as it's commonly used in templates.
        """
        return list(self.get_descendants()) + [self]

    def has_children(self):
        return self.get_num_children() > 0

    def get_num_children(self):
        return self.get_children().count()

    def get_values(self):
        return {
            'name': self.name,
            'icon': self.get_icon(),
            'absolute_url': self.get_absolute_url(),
            'slug': self.slug,
            'image_banner': self.get_image_banner(),
            'link_banner': self.link_banner,
        }

    def get_image_banner(self):
        image_banner = ''

        if self.image_banner:
            options = {'size': (544, 212), 'crop': True}
            image_banner = get_thumbnailer(self.image_banner).get_thumbnail(options).url
        return image_banner

    def get_absolute_url(self, values={}):
        """
        Our URL scheme means we have to look up the category's ancestors. As
        that is a bit more expensive, we cache the generated URL. That is
        safe even for a stale cache, as the default implementation of
        ProductCategoryView does the lookup via primary key anyway. But if
        you change that logic, you'll have to reconsider the caching
        approach.
        """
        dict_values = {'category_slug': self.full_slug}

        if values.get('filter_slug'):
            dict_values.update({'filter_slug': values.get('filter_slug')})

        if values.get('page') and int(values.get('page')) != 1:
            dict_values.update({'page': values.get('page')})

        if values.get('sort'):
            dict_values.update({'sort': values.get('sort')})

        return reverse('catalogue:category', kwargs=dict_values)

    @classmethod
    def get_annotated_list_qs_depth(cls, parent=None, max_depth=None):
        """
        Gets an annotated list from a tree branch, change queryset

        :param parent:

            The node whose descendants will be annotated. The node itself            will be included in the list. If not given, the entire tree
            will be annotated.

        :param max_depth:

            Optionally limit to specified depth

        :sort_order

            Sort order queryset.

        """

        result, info = [], {}
        start_depth, prev_depth = (None, None)
        qs = cls.get_tree(parent)
        if max_depth:
            qs = qs.filter(depth__lte=max_depth)
        return cls.get_annotated_list_qs(qs)

    @classmethod
    def dump_bulk_depth(cls, parent=None, keep_ids=True, max_depth=3):
        """
        Dumps a tree branch to a python type structure.

        Args:
            parent: by default None (if you set the Parent to the object category then we obtain a tree search)
            keep_ids: by default True (if True add id category in data)
            max_depth: by default 3 (max depth in category tree) (if max_depth = 0 return all tree)

        Returns:
        [{'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
                {'data': category.get_values()},
                {'data': category.get_values(), 'children':[
                    {'data': category.get_values()},
                ]},
                {'data': category.get_values()},
            ]},
            {'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
            ]},
        ]
        """
        # Because of fix_tree, this method assumes that the depth
        # and numchild properties in the nodes can be incorrect,
        # so no helper methods are used
        data = cls.get_annotated_list_qs_depth(max_depth=max_depth)
        ret, lnk = [], {}

        for pyobj, info in data:
            # django's serializer stores the attributes in 'fields'
            path = pyobj.path
            depth = int(len(path) / cls.steplen)
            # this will be useless in load_bulk

            newobj = {'data': pyobj.get_values()}

            if keep_ids:
                newobj['id'] = pyobj.pk

            if (not parent and depth == 1) or \
                    (parent and len(path) == len(parent.path)):
                ret.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = lnk[parentpath]
                if 'children' not in parentobj:
                    parentobj['children'] = []
                parentobj['children'].append(newobj)
            lnk[path] = newobj
        return ret

    def get_icon(self):
        icon = ''

        if self.icon:
            options = {'size': (50, 31), 'crop': True}
            icon = get_thumbnailer(self.icon).get_thumbnail(options).url
        return icon


@python_2_unicode_compatible
class AbstractProductVersion(models.Model, CommonFeatureProduct):
    attributes = models.ManyToManyField('catalogue.Feature', through='catalogue.VersionAttribute',
                                        verbose_name=_('Attributes'), related_name='product_versions')
    product = models.ForeignKey('catalogue.Product', related_name='versions', on_delete=models.DO_NOTHING)
    price_retail = models.DecimalField(_("Price (retail)"), decimal_places=2, max_digits=12)
    cost_price = models.DecimalField(_("Cost Price"), decimal_places=2, max_digits=12)

    class Meta:
        abstract = True
        ordering = ('product', 'price_retail', )
        app_label = 'catalogue'
        verbose_name = _('Product version')
        verbose_name_plural = _('Product versions')

    def __str__(self):
        return u'{}, Version of product - {}'.format(self.pk, getattr(self, 'product', None))


@python_2_unicode_compatible
class AbstractVersionAttribute(models.Model):
    version = models.ForeignKey('catalogue.ProductVersion', verbose_name=_('Version of product'),
                                related_name='version_attributes')
    attribute = models.ForeignKey('catalogue.Feature', verbose_name=_('Attribute'),
                                  related_name='version_attributes')
    price_retail = models.DecimalField(_("Price (retail)"), decimal_places=2, max_digits=12, blank=True, default=0)
    cost_price = models.DecimalField(_("Cost Price"), decimal_places=2, max_digits=12, blank=True, default=0)

    class Meta:
        abstract = True
        unique_together = ('version', 'attribute', )
        app_label = 'catalogue'
        verbose_name = _('Version attribute')
        verbose_name_plural = _('Version attributes')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, self.version.product.title, self.attribute.title)

    def save(self, **kwargs):
        product_versions = self.version._meta.model.objects.filter(product=self.version.product)
        search_attributes = (sorted(attr.pk for attr in product_version.attributes.all()) for product_version in product_versions)
        current_attributes = list(self.version.attributes.all()) + [self.attribute]
        current_attributes = sorted([attr.pk for attr in current_attributes])

        if current_attributes in search_attributes:
            raise IntegrityError(u'UNIQUE constraint failed: catalogue_productversion.version_id, catalogue_productversion.attribute_id'.format(self.attribute))
        super(AbstractVersionAttribute, self).save(**kwargs)


@python_2_unicode_compatible
class AbstractProductFeature(models.Model, CommonFeatureProduct):
    sort = models.IntegerField(_('Sort'), blank=True, null=True, default=0)
    info = models.CharField(_('Block info'), max_length=255, blank=True)
    product = models.ForeignKey('catalogue.Product', verbose_name=_('Product'), related_name='product_features',
                                on_delete=models.DO_NOTHING)
    feature = models.ForeignKey('catalogue.Feature', verbose_name=_('Feature'), related_name='product_features',
                                on_delete=models.DO_NOTHING)
    non_standard = models.BooleanField(verbose_name=_('Available non standard size for this feature'), default=False)
    image = FilerImageField(verbose_name=_("Image"), null=True, blank=True, related_name="image")
    product_with_images = models.ManyToManyField('catalogue.Product', verbose_name=_('Product with images.'),
                                                 related_name='product_feature', blank=True)

    class Meta:
        abstract = True
        unique_together = ('product', 'feature', )
        ordering = ['sort', 'feature__title']
        app_label = 'catalogue'
        verbose_name = _('Product feature')
        verbose_name_plural = _('Product features')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, self.product.title, self.feature.title)

    def clean(self):
        if self.non_standard is True:
            if self.feature.bottom_line is None:
                raise ValidationError(_('For this feature not specified bottom_line.'))

            if self.feature.top_line is None:
                raise ValidationError(_('For this feature not specified top_line.'))

            if self.product.non_standard_price_retail == 0:
                raise ValidationError(_('For this product set non_standard_price_retail to 0.'))

    def save(self, *args, **kwargs):
        if self.non_standard is True:
            if self.feature.bottom_line is None:
                raise Exception('For feature - "{}" not specified bottom_line.'.format(self.feature))

            if self.feature.top_line is None:
                raise Exception('For feature - "{}" not specified top_line.'.format(self.feature))

            if self.product.non_standard_price_retail == 0:
                raise Exception('For product - "{}" set non_standard_price_retail to 0.'.format(self.product))

        super(AbstractProductFeature, self).save(*args, **kwargs)


@python_2_unicode_compatible
class AbstractProductOptions(models.Model):
    product = models.ForeignKey('catalogue.Product', related_name='product_options')
    option = models.ForeignKey('catalogue.Feature', related_name='product_options')
    plus = models.BooleanField(verbose_name=_('Plus on price'), default=False)
    percent = models.IntegerField(verbose_name=_('Percent'), null=True, blank=True, default=0)
    price_retail = models.DecimalField(_("Price (retail)"), decimal_places=2, max_digits=12)
    cost_price = models.DecimalField(_("Cost Price"), decimal_places=2, max_digits=12)

    class Meta:
        abstract = True
        app_label = 'catalogue'
        unique_together = ('product', 'option', )
        verbose_name = _('Product option')
        verbose_name_plural = _('Product options')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, self.product.title, self.option.title)
