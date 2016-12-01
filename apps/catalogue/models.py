from django.db.models import Prefetch
from apps.partner.models import StockRecord
from django.contrib.contenttypes import fields
import os
from django.utils import six
from datetime import datetime, date
from django.utils.safestring import mark_safe
from django.conf import settings
from django.core.files.base import File
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.contrib.contenttypes.models import ContentType
from oscar.core.utils import slugify
from oscar.core.validators import non_python_keyword
from oscar.core.loading import get_model
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import MEDIA_ROOT
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from filer.fields.image import FilerImageField
import logging
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags
from soloha.core.utils import CommonFeatureProduct
from apps.partner.models import Partner
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from oscar.core.decorators import deprecated


REGEXP_PHONE = r'/^((8|\+38)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$/'
REGEXP_EMAIL = r'/^[-\w.]+@([A-z0-9][-A-z0-9]+\.)+[A-z]{2,4}$/'


class ProductiveCategoryQuerySet(models.QuerySet):
    @property
    def parent(self):
        return 'parent'

    @property
    def parent_double(self):
        return '{0}__{0}'.format(self.parent)

    def prefetch(self, children, grandchildren):
        return self.prefetch_related(
            Prefetch('children', queryset=children),
            Prefetch('children__children', queryset=grandchildren),
        )

    def select_main_menu(self):
        return self.select_related('image_banner', 'icon')

    def select_product_url(self):
        return self.select_related(self.parent_double)

    def select_children(self):
        return self.select_related(self.parent)

    def select_grandchildren(self):
        return self.select_related(self.parent_double)

    def select_page(self):
        return self.select_related('image', self.parent_double)

    def included(self):
        return self.filter(enable=True)

    def hi(self):
        return self.filter(level=0)

    def order_simple(self):
        return self.order_by()

    def only_page(self):
        return self.only(
            'slug', 'name', 'h1', 'slug', 'meta_title', 'meta_description', 'meta_keywords', 'description',
            'image__file_ptr__file',
            "image__file_ptr__original_filename",
            "image__file_ptr__name",
            "image__is_public",
            'image__id',
            'parent_id',
        )

    def only_menu(self):
        return self.only(
            'slug',
            'name',
            'parent_id',
            "icon__id",
            'icon__file_ptr__file',
            "icon__file_ptr__original_filename",
            "icon__file_ptr__name",
            "icon__is_public",
            'image_banner__file_ptr__file',
            "image_banner__file_ptr__original_filename",
            "image_banner__file_ptr__name",
            "image_banner__is_public",
            'image_banner__id',
            'link_banner'
        )

    def only_children(self):
        return self.only('slug', 'name', 'parent_id')

    def only_product_url(self):
        return self.only('slug', 'parent_id')

    def only_parent(self):
        return self.only('parent_id')

    def only_simple(self):
        return self.only('id')


class ProductiveCategoryManager(models.Manager):
    def get_queryset(self):
        return ProductiveCategoryQuerySet(self.model, using=self._db)

    def common(self):
        return self.get_queryset().included().only_simple().order_simple()

    def menu(self):
        return self.common().hi().select_main_menu().prefetch(
            children=self.children(),
            grandchildren=self.grandchildren()
        ).only_menu()

    def children(self):
        return self.common().select_children().only_children()

    def grandchildren(self):
        return self.common().select_grandchildren().only_children()

    def product_url(self):
        return self.common().select_product_url().only_product_url()

    def page(self):
        return self.common().select_page().prefetch(
            children=self.common().only_parent(),
            grandchildren=self.common().only_parent()
        ).only_page()


class ProductiveFeatureManager(models.Manager):
    def browse(self):
        return self.get_queryset().select_related('parent').only(
            'title', 'parent'
        ).order_by()

    def simple(self):
        return self.get_queryset().only(
            'id',
        ).order_by()


class ProductiveProductQuerySet(models.QuerySet):
    def included(self):
        return self.filter(enable=True)

    def prefetch_list(self):
        return self.prefetch_related(
            Prefetch('categories', queryset=Category.objects.product_url()),
            Prefetch('stockrecords', queryset=StockRecord.objects.browse()),
            Prefetch('characteristics', queryset=Feature.objects.browse()),
            Prefetch('images', queryset=ProductImage.objects.browse()),
            Prefetch('children', queryset=Product.objects.select_related('parent').only('id', 'parent').order_by(
                'stockrecords__{}'.format(StockRecord.order_by_price()))),
            Prefetch('children__stockrecords', queryset=StockRecord.objects.browse()),
        )

    def only_list(self):
        return self.only(
            'title',
            'slug',
            'product_class__id',
            'product_class__track_stock',
            'product_class__slug',
            'structure',
            'upc',
        )

    def order_simple(self):
        return self.order_by()

    def select_list(self):
        return self.select_related('product_class')

    def canonical(self):
        return self.filter(parent=None)


class ProductiveProductManager(models.Manager):
    def get_queryset(self):
        return ProductiveProductQuerySet(self.model, using=self._db)

    def common(self):
        return self.get_queryset().included().order_simple()

    def list(self):
        return self.common().select_list().prefetch_list().only_list()

    def promotions(self):
        return self.common().canonical().select_list().prefetch_list().only_list()


class MissingProductImage(object):

    """
    Mimics a Django file field by having a name property.

    sorl-thumbnail requires all it's images to be in MEDIA_ROOT. This class
    tries symlinking the default "missing image" image in STATIC_ROOT
    into MEDIA_ROOT for convenience, as that is necessary every time an Oscar
    project is setup. This avoids the less helpful NotFound IOError that would
    be raised when sorl-thumbnail tries to access it.
    """

    def __init__(self, name=None):
        self.name = name if name else settings.OSCAR_MISSING_IMAGE_URL
        media_file_path = os.path.join(settings.MEDIA_ROOT, self.name)
        # don't try to symlink if MEDIA_ROOT is not set (e.g. running tests)
        if settings.MEDIA_ROOT and not os.path.exists(media_file_path):
            self.symlink_missing_image(media_file_path)

    @property
    def original(self):
        return self.name

    @property
    def is_missing(self):
        return True

    def symlink_missing_image(self, media_file_path):
        static_file_path = find('oscar/img/%s' % self.name)
        if static_file_path is not None:
            try:
                os.symlink(static_file_path, media_file_path)
            except OSError:
                raise ImproperlyConfigured((
                    "Please copy/symlink the "
                    "'missing image' image at %s into your MEDIA_ROOT at %s. "
                    "This exception was raised because Oscar was unable to "
                    "symlink it for you.") % (media_file_path,
                                              settings.MEDIA_ROOT))
            else:
                logging.info((
                    "Symlinked the 'missing image' image at %s into your "
                    "MEDIA_ROOT at %s") % (media_file_path,
                                           settings.MEDIA_ROOT))


@python_2_unicode_compatible
class Option(models.Model):
    """
    An option that can be selected for a particular item when the product
    is added to the basket.

    For example,  a list ID for an SMS message send, or a personalised message
    to print on a T-shirt.

    This is not the same as an 'attribute' as options do not have a fixed value
    for a particular item.  Instead, option need to be specified by a customer
    when they add the item to their basket.
    """
    name = models.CharField(_("Name"), max_length=128)
    code = models.SlugField(_("Code"), max_length=128, unique=True)
    REQUIRED, OPTIONAL = ('Required', 'Optional')
    TYPE_CHOICES = (
        (REQUIRED, _("Required - a value for this option must be specified")),
        (OPTIONAL, _("Optional - a value for this option can be omitted")),
    )
    type = models.CharField(_("Status"), max_length=128, default=REQUIRED, choices=TYPE_CHOICES)

    class Meta:
        app_label = 'catalogue'
        verbose_name = _("Option")
        verbose_name_plural = _("Options")

    def __str__(self):
        return self.name

    @property
    def is_required(self):
        return self.type == self.REQUIRED


@python_2_unicode_compatible
class ProductClass(models.Model):
    """
    Used for defining options and attributes for a subset of products.
    E.g. Books, DVDs and Toys. A product can only belong to one product class.

    At least one product class must be created when setting up a new
    Oscar deployment.

    Not necessarily equivalent to top-level categories but usually will be.
    """
    name = models.CharField(_('Name'), max_length=128)
    slug = models.SlugField(_('Slug'), max_length=128, unique=True)

    #: Some product type don't require shipping (eg digital products) - we use
    #: this field to take some shortcuts in the checkout.
    requires_shipping = models.BooleanField(_("Requires shipping?"), default=True)

    #: Digital products generally don't require their stock levels to be
    #: tracked.
    track_stock = models.BooleanField(_("Track stock levels?"), default=True)

    #: These are the options (set by the user when they add to basket) for this
    #: item class.  For instance, a product class of "SMS message" would always
    #: require a message to be specified before it could be bought.
    #: Note that you can also set options on a per-product level.
    options = models.ManyToManyField(Option, blank=True, verbose_name=_("Options"))

    class Meta:
        app_label = 'catalogue'
        ordering = ['name']
        verbose_name = _("Product class")
        verbose_name_plural = _("Product classes")

    def __str__(self):
        return self.name

    @property
    def has_attributes(self):
        return self.attributes.exists()


@python_2_unicode_compatible
class Category(MPTTModel):
    name = models.CharField(_('Name'), max_length=300, db_index=True)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=400, unique=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True, db_index=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=310)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=480)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    sort = models.IntegerField(blank=True, null=True, default=0, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    link_banner = models.URLField(_('Link banner'), blank=True, null=True, max_length=555)
    description = RichTextUploadingField(_('Description'), blank=True)
    image_banner = FilerImageField(verbose_name=_('Image banner'), blank=True, null=True, related_name='category_image_banner')
    icon = FilerImageField(verbose_name=_('Icon'), blank=True, null=True, related_name='category_icon')
    image = FilerImageField(verbose_name=_('Image'), null=True, blank=True, related_name="category_image")
    _slug_separator = '/'
    _full_name_separator = ' > '
    objects = ProductiveCategoryManager()

    class MPTTMeta:
        order_insertion_by = ('sort', 'name', )

    class Meta:
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

    @cached_property
    def full_slug(self):
        """
        Returns a string of this category's slug concatenated with the slugs
        of it's ancestors, e.g. 'books/non-fiction/essential-programming'.

        Oscar used to store this as in the 'slug' model field, but this field
        has been re-purposed to only store this category's slug and to not
        include it's ancestors' slugs.
        """
        slugs = [str(category.slug) for category in self.get_ancestors_through_parent(include_self=True)]
        return self._slug_separator.join(slugs)

    def get_descendants_through_children(self):
        children = list(self.children.all())

        for category in children[:]:
            children += list(category.children.all())

        return children + [self]

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
        if obj.parent_id is not None:
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

    def get_meta_title(self):
        return self.meta_title or self.name

    def get_h1(self):
        return self.h1 or self.name

    def get_meta_description(self):
        return self.meta_description or truncatechars(strip_tags(self.description), 100)

    @cached_property
    def get_absolute_url(self):
        """
        Our URL scheme means we have to look up the category's ancestors. As
        that is a bit more expensive, we cache the generated URL. That is
        safe even for a stale cache, as the default implementation of
        ProductCategoryView does the lookup via primary key anyway. But if
        you change that logic, you'll have to reconsider the caching
        approach.
        """
        dict_values = {'category_slug': self.full_slug}

        if getattr(self, 'filter_slug_objects', False):
            filter_slug = self.filter_slug_objects.values_list('slug', flat=True)
            filter_slug = AbstractFeature.slug_separator.join(filter_slug)

            dict_values.update(
                {
                    'filter_slug': filter_slug
                }
            )

        if getattr(self, 'page', None) is not None and int(self.page) != 1:
            dict_values.update({'page': self.page})

        if getattr(self, 'order', None) is not None:
            dict_values.update({'sort': self.order})

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
class Feature(MPTTModel):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(verbose_name=_('Slug'), max_length=255, unique=True, blank=True, db_index=True)
    parent = TreeForeignKey('self', verbose_name=_('Parent'), related_name='children', blank=True, null=True, db_index=True)
    sort = models.IntegerField(blank=True, null=True, default=0, db_index=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    bottom_line = models.IntegerField(verbose_name=_('Bottom line size'), blank=True, null=True)
    top_line = models.IntegerField(verbose_name=_('Top line size'), blank=True, null=True)
    slug_separator = '/'
    objects = ProductiveFeatureManager()

    class MPTTMeta:
        order_insertion_by = ('sort', 'title', )

    class Meta:
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

    @property
    def parent_pk(self):
        parent = self.parent

        if parent:
            return parent.pk

    def get_values(self, *names_fields):
        """
        get values by name field
        :param names_fields: name fields in this object
        :return: dict
        Example
            {'pk': 1, title: 'Feature'}
        """
        data = {}
        for name_field in names_fields:
            key = 'parent' if name_field == 'parent_pk' else name_field
            data[key] = getattr(self, name_field)
        return data


@python_2_unicode_compatible
class Product(models.Model, CommonFeatureProduct):
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
    partner = models.ForeignKey(Partner, verbose_name=_("Partner"), related_name='products', null=True)

    STANDALONE, PARENT, CHILD = 'standalone', 'parent', 'child'
    STRUCTURE_CHOICES = (
        (STANDALONE, _('Stand-alone product')),
        (PARENT, _('Parent product')),
        (CHILD, _('Child product'))
    )
    structure = models.CharField(
        _("Product structure"), max_length=10, choices=STRUCTURE_CHOICES, default=STANDALONE
    )

    upc = models.CharField(
        _("UPC"), max_length=64, blank=True, unique=True, help_text=_(
            "Universal Product Code (UPC) is an identifier for a product which is not specific to a particular "
            " supplier. Eg an ISBN for a book."
        )
    )

    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='children',
        verbose_name=_("Parent product"),
        help_text=_("Only choose a parent product if you're creating a child "
                    "product.  For example if this is a size "
                    "4 of a particular t-shirt.  Leave blank if this is a "
                    "stand-alone product (i.e. there is only one version of"
                    " this product).")
    )

    date_created = models.DateTimeField(_("Date created"), auto_now_add=True, db_index=True)

    # This field is used by Haystack to reindex search
    date_updated = models.DateTimeField(
        _("Date updated"), auto_now=True, db_index=True
    )

    categories = models.ManyToManyField(Category, related_name="products", verbose_name=_("Categories"))
    filters = models.ManyToManyField(Feature, related_name="filter_products", verbose_name=_('Filters of product'), blank=True)
    attributes = models.ManyToManyField(Feature, through='catalogue.ProductFeature', verbose_name=_('Attribute of product'), related_name="attr_products", blank=True)
    characteristics = models.ManyToManyField(Feature, verbose_name='Characteristics', related_name='characteristic_products', blank=True)
    options = models.ManyToManyField(Feature, through='catalogue.ProductOptions', related_name='option_products', verbose_name='Additional options')

    non_standard_price_retail = models.DecimalField(_("Non-standard retail price"), decimal_places=2, max_digits=12, blank=True, default=0)
    non_standard_cost_price = models.DecimalField(_("Non-standard cost price"), decimal_places=2, max_digits=12, blank=True, default=0)

    #: "Kind" of product, e.g. T-Shirt, Book, etc.
    #: None for child products, they inherit their parent's product class
    product_class = models.ForeignKey(
        ProductClass, on_delete=models.PROTECT,
        verbose_name=_('Product type'), related_name="products",
        help_text=_("Choose what type of product this is")
    )
    recommended_products = models.ManyToManyField(
        'self', through='catalogue.ProductRecommendation', blank=True,
        verbose_name=_("Recommended products"),
        help_text=_("These are products that are recommended to accompany the "
                    "main product.")
    )

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
            "or not")
    )

    separator = ','

    class Meta:
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

    @cached_property
    def get_absolute_url(self):
        """
        Return a product's absolute url
        """
        dict_values = {'product_slug': self.slug}

        if self.categories.all():
            dict_values.update({'category_slug': self.categories.all()[0].full_slug})
            # dict_values.update({'category_slug': self.categories.all()[0].slug})

        return reverse('catalogue:detail', kwargs=dict_values)

    def categories_to_str(self):
        return self.separator.join([category.name for category in self.get_categories().all()])
    categories_to_str.short_description = _("Categories")

    def partners_to_str(self):
        return self.partner
    categories_to_str.short_description = _("Partner")

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
        if not getattr(self, 'product_class', False):
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

    def _clean_parent(self):
        """
        Validates a parent product.
        """
        self._clean_standalone()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.get_title())

        super(AbstractProduct, self).save(*args, **kwargs)
        self.characteristics.add(*self.filters.all())

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

    def get_stockrecord(self, request):
        stockrecord = request.strategy

        if self.is_parent:
            obj, stockrecord = stockrecord.select_children_stockrecords(self)[0]
        else:
            stockrecord = stockrecord.select_stockrecord(self)

        return stockrecord

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

    def get_h1(self):
        return self.h1 or self.get_title()

    def get_meta_title(self):
        return self.meta_title or self.get_title()

    def get_meta_description(self):
        return self.meta_description or truncatechars(strip_tags(self.description), 100)

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

    def images_all(self):
        images = [image.image for image in self.images.all()]
        images = filter(lambda image: getattr(image, 'is_missing', False) is False, images)
        return [self.get_missing_image()] if not images else images

    @staticmethod
    def get_missing_image():
        """
        Returns a missing image object.
        """
        # This class should have a 'name' property so it mimics the Django file
        # field.
        return MissingProductImage()

    def thumb(self, image=None):
        return super(AbstractProduct, self).thumb(image=self.primary_image())

    def primary_image(self):
        """
        Returns the primary image for a product. Usually used when one can
        only display one product image, e.g. in a list of products.
        """
        return self.images.all()[0].image if self.images.all() else self.get_missing_image()

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


@python_2_unicode_compatible
class ProductFeature(models.Model, CommonFeatureProduct):
    sort = models.IntegerField(_('Sort'), blank=True, null=True, default=0)
    info = models.CharField(_('Block info'), max_length=255, blank=True)
    product = models.ForeignKey(
        Product, verbose_name=_('Product'), related_name='product_features', on_delete=models.DO_NOTHING
    )
    feature = models.ForeignKey(
        Feature, verbose_name=_('Feature'), related_name='product_features', on_delete=models.DO_NOTHING
    )
    non_standard = models.BooleanField(verbose_name=_('Available non standard size for this feature'), default=False)
    image = FilerImageField(verbose_name=_("Image"), null=True, blank=True, related_name="image")
    product_with_images = models.ManyToManyField(
        Product, verbose_name=_('Product with images.'), related_name='product_feature', blank=True
    )

    class Meta:
        unique_together = ('product', 'feature', )
        ordering = ['sort', 'feature__title']
        app_label = 'catalogue'
        verbose_name = _('Product feature')
        verbose_name_plural = _('Product features')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, getattr(self, 'product.title', None), getattr(self, 'feature.title', None))

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

        super(ProductFeature, self).save(*args, **kwargs)


@python_2_unicode_compatible
class ProductOptions(models.Model):
    product = models.ForeignKey(Product, related_name='product_options')
    option = models.ForeignKey(Feature, related_name='product_options')
    plus = models.BooleanField(verbose_name=_('Plus on price'), default=False)
    percent = models.IntegerField(verbose_name=_('Percent'), null=True, blank=True, default=0)
    price_retail = models.DecimalField(_("Price (retail)"), decimal_places=2, max_digits=12)
    cost_price = models.DecimalField(_("Cost Price"), decimal_places=2, max_digits=12)

    class Meta:
        app_label = 'catalogue'
        unique_together = ('product', 'option',)
        verbose_name = _('Product option')
        verbose_name_plural = _('Product options')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, self.product.title, self.option.title)


@python_2_unicode_compatible
class ProductRecommendation(models.Model, CommonFeatureProduct):
    """
    'Through' model for product recommendations
    """
    primary = models.ForeignKey(Product, related_name='primary_recommendations', verbose_name=_("Primary product"))
    recommendation = models.ForeignKey(Product, verbose_name=_("Recommended product"))
    ranking = models.PositiveSmallIntegerField(
        _('Ranking'), default=0,
        help_text=_(
            'Determines order of the products. A product with a higher value will appear before one with a '
            'lower ranking.'
        )
    )

    class Meta:
        app_label = 'catalogue'
        ordering = ['primary', '-ranking']
        unique_together = ('primary', 'recommendation')
        verbose_name = _('Product recommendation')
        verbose_name_plural = _('Product recomendations')

    def __init__(self, *args, **kwargs):
        super(ProductRecommendation, self).__init__(*args, **kwargs)
        self.product = getattr(self, 'primary', None)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.ranking is None:
            self.ranking = 0
        super(ProductRecommendation, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                                update_fields=update_fields)

    def recommendation_thumb(self):
        return self.recommendation.thumb()
    recommendation_thumb.allow_tags = True
    recommendation_thumb.short_description = _('Image of recommendation product.')


@python_2_unicode_compatible
class ProductAttribute(models.Model):
    """
    Defines an attribute for a product class. (For example, number_of_pages for
    a 'book' class)
    """
    product_class = models.ForeignKey(
        ProductClass, related_name='attributes', blank=True, null=True, verbose_name=_("Product type")
    )
    name = models.CharField(_('Name'), max_length=128)
    code = models.SlugField(
        _('Code'), max_length=128,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z_][0-9a-zA-Z_]*$',
                message=_(
                    "Code can only contain the letters a-z, A-Z, digits, "
                    "and underscores, and can't start with a digit")),
            non_python_keyword
        ])

    # Attribute types
    TEXT = "text"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    FLOAT = "float"
    RICHTEXT = "richtext"
    DATE = "date"
    OPTION = "option"
    ENTITY = "entity"
    FILE = "file"
    IMAGE = "image"
    TYPE_CHOICES = (
        (TEXT, _("Text")),
        (INTEGER, _("Integer")),
        (BOOLEAN, _("True / False")),
        (FLOAT, _("Float")),
        (RICHTEXT, _("Rich Text")),
        (DATE, _("Date")),
        (OPTION, _("Option")),
        (ENTITY, _("Entity")),
        (FILE, _("File")),
        (IMAGE, _("Image")),
    )
    type = models.CharField(
        choices=TYPE_CHOICES, default=TYPE_CHOICES[0][0],
        max_length=20, verbose_name=_("Type"))

    option_group = models.ForeignKey(
        AttributeOptionGroup, blank=True, null=True,
        verbose_name=_("Option Group"),
        help_text=_('Select an option group if using type "Option"'))
    required = models.BooleanField(_('Required'), default=False)

    class Meta:
        app_label = 'catalogue'
        ordering = ['code']
        verbose_name = _('Product attribute')
        verbose_name_plural = _('Product attributes')

    @property
    def is_option(self):
        return self.type == self.OPTION

    @property
    def is_file(self):
        return self.type in [self.FILE, self.IMAGE]

    def __str__(self):
        return self.name

    def save_value(self, product, value):
        ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
        try:
            value_obj = product.attribute_values.get(attribute=self)
        except ProductAttributeValue.DoesNotExist:
            # FileField uses False for announcing deletion of the file
            # not creating a new value
            delete_file = self.is_file and value is False
            if value is None or value == '' or delete_file:
                return
            value_obj = ProductAttributeValue.objects.create(
                product=product, attribute=self)

        if self.is_file:
            # File fields in Django are treated differently, see
            # django.db.models.fields.FileField and method save_form_data
            if value is None:
                # No change
                return
            elif value is False:
                # Delete file
                value_obj.delete()
            else:
                # New uploaded file
                value_obj.value = value
                value_obj.save()
        else:
            if value is None or value == '':
                value_obj.delete()
                return
            if value != value_obj.value:
                value_obj.value = value
                value_obj.save()

    def validate_value(self, value):
        validator = getattr(self, '_validate_%s' % self.type)
        validator(value)

    # Validators

    def _validate_text(self, value):
        if not isinstance(value, six.string_types):
            raise ValidationError(_("Must be str or unicode"))

    _validate_richtext = _validate_text

    def _validate_float(self, value):
        try:
            float(value)
        except ValueError:
            raise ValidationError(_("Must be a float"))

    def _validate_integer(self, value):
        try:
            int(value)
        except ValueError:
            raise ValidationError(_("Must be an integer"))

    def _validate_date(self, value):
        if not (isinstance(value, datetime) or isinstance(value, date)):
            raise ValidationError(_("Must be a date or datetime"))

    def _validate_boolean(self, value):
        if not type(value) == bool:
            raise ValidationError(_("Must be a boolean"))

    def _validate_entity(self, value):
        if not isinstance(value, models.Model):
            raise ValidationError(_("Must be a model instance"))

    def _validate_option(self, value):
        if not isinstance(value, get_model('catalogue', 'AttributeOption')):
            raise ValidationError(
                _("Must be an AttributeOption model object instance"))
        if not value.pk:
            raise ValidationError(_("AttributeOption has not been saved yet"))
        valid_values = self.option_group.options.values_list(
            'option', flat=True)
        if value.option not in valid_values:
            raise ValidationError(
                _("%(enum)s is not a valid choice for %(attr)s") %
                {'enum': value, 'attr': self})

    def _validate_file(self, value):
        if value and not isinstance(value, File):
            raise ValidationError(_("Must be a file field"))

    _validate_image = _validate_file


@python_2_unicode_compatible
class ProductAttributeValue(models.Model):
    """
    The "through" model for the m2m relationship between catalogue.Product and
    catalogue.ProductAttribute.  This specifies the value of the attribute for
    a particular product

    For example: number_of_pages = 295
    """
    attribute = models.ForeignKey(ProductAttribute, verbose_name=_("Attribute"))
    product = models.ForeignKey(Product, related_name='attribute_values', verbose_name=_("Product"))
    value_text = models.TextField(_('Text'), blank=True, null=True)
    value_integer = models.IntegerField(_('Integer'), blank=True, null=True)
    value_boolean = models.NullBooleanField(_('Boolean'), blank=True)
    value_float = models.FloatField(_('Float'), blank=True, null=True)
    value_richtext = models.TextField(_('Richtext'), blank=True, null=True)
    value_date = models.DateField(_('Date'), blank=True, null=True)
    value_option = models.ForeignKey(AttributeOption, blank=True, null=True, verbose_name=_("Value option"))
    value_file = models.FileField(upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255, blank=True, null=True)
    value_image = models.ImageField(upload_to=settings.OSCAR_IMAGE_FOLDER, max_length=255, blank=True, null=True)
    value_entity = fields.GenericForeignKey('entity_content_type', 'entity_object_id')

    entity_content_type = models.ForeignKey(ContentType, null=True, blank=True, editable=False)
    entity_object_id = models.PositiveIntegerField(
        null=True, blank=True, editable=False)

    def _get_value(self):
        return getattr(self, 'value_%s' % self.attribute.type)

    def _set_value(self, new_value):
        if self.attribute.is_option and isinstance(new_value, six.string_types):
            # Need to look up instance of AttributeOption
            new_value = self.attribute.option_group.options.get(
                option=new_value)
        setattr(self, 'value_%s' % self.attribute.type, new_value)

    value = property(_get_value, _set_value)

    class Meta:
        app_label = 'catalogue'
        unique_together = ('attribute', 'product')
        verbose_name = _('Product attribute value')
        verbose_name_plural = _('Product attribute values')

    def __str__(self):
        return self.summary()

    def summary(self):
        """
        Gets a string representation of both the attribute and it's value,
        used e.g in product summaries.
        """
        return u"%s: %s" % (self.attribute.name, self.value_as_text)

    @property
    def value_as_text(self):
        """
        Returns a string representation of the attribute's value. To customise
        e.g. image attribute values, declare a _image_as_text property and
        return something appropriate.
        """
        property_name = '_%s_as_text' % self.attribute.type
        return getattr(self, property_name, self.value)

    @property
    def _richtext_as_text(self):
        return strip_tags(self.value)

    @property
    def _entity_as_text(self):
        """
        Returns the unicode representation of the related model. You likely
        want to customise this (and maybe _entity_as_html) if you use entities.
        """
        return six.text_type(self.value)

    @property
    def value_as_html(self):
        """
        Returns a HTML representation of the attribute's value. To customise
        e.g. image attribute values, declare a _image_as_html property and
        return e.g. an <img> tag.  Defaults to the _as_text representation.
        """
        property_name = '_%s_as_html' % self.attribute.type
        return getattr(self, property_name, self.value_as_text)

    @property
    def _richtext_as_html(self):
        return mark_safe(self.value)


@python_2_unicode_compatible
class AttributeOptionGroup(models.Model):
    """
    Defines a group of options that collectively may be used as an
    attribute type

    For example, Language
    """
    name = models.CharField(_('Name'), max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'catalogue'
        verbose_name = _('Attribute option group')
        verbose_name_plural = _('Attribute option groups')

    @property
    def option_summary(self):
        options = [o.option for o in self.options.all()]
        return ", ".join(options)


@python_2_unicode_compatible
class AttributeOption(models.Model):
    """
    Provides an option within an option group for an attribute type
    Examples: In a Language group, English, Greek, French
    """
    group = models.ForeignKey(AttributeOptionGroup, related_name='options', verbose_name=_("Group"))
    option = models.CharField(_('Option'), max_length=255)

    def __str__(self):
        return self.option

    class Meta:
        app_label = 'catalogue'
        verbose_name = _('Attribute option')
        verbose_name_plural = _('Attribute options')


class ProductiveProductImageManager(models.Manager):
    def browse(self):
        return self.get_queryset().select_related('original').only(
            'original__id',
            'original__file_ptr__file',
            "original__is_public",
            'product__title',
            'product__id',
            'caption',
        ).order_by('display_order')


@python_2_unicode_compatible
class ProductImage(models.Model, CommonFeatureProduct):
    """
    An image of a product
    """
    product = models.ForeignKey(Product, related_name='images', verbose_name=_("Product"))
    original = FilerImageField(verbose_name=_("Original"), null=True, blank=True, related_name="original")
    caption = models.CharField(_("Caption"), max_length=200, blank=True)
    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(
        _("Display order"), default=0, help_text=_(
            "An image with a display order of zero will be the primary image for a product"
        )
    )
    date_created = models.DateTimeField(_("Date created"), auto_now_add=True)
    objects = ProductiveProductImageManager()

    class Meta:
        app_label = 'catalogue'
        # Any custom models should ensure that this ordering is unchanged, or
        # your query count will explode. See AbstractProduct.primary_image.
        ordering = ("product", "display_order",)
        unique_together = ("product", "display_order")
        verbose_name = _('Product image')
        verbose_name_plural = _('Product images')

    def __str__(self):
        return u"Image of '%s'" % getattr(self, 'product', None)

    @property
    def name(self):
        return self.original.file.name if self.original else ''

    @property
    def image(self):
        return self.check_exist_image()

    def is_primary(self):
        """
        Return bool if image display order is 0
        """
        return self.display_order == 0

    def thumb(self, image=None):
        return super(ProductImage, self).thumb(image=self.image)

    def check_exist_image(self):
        current_path = os.getcwd()
        os.chdir(MEDIA_ROOT)
        abs_path = os.path.abspath(self.name)
        image = self

        if not self.name or not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            image = self.product.get_missing_image()

        os.chdir(current_path)
        return image

    def get_caption(self):
        return self.caption or self.product.get_title()

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
