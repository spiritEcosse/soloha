from oscar.core.loading import is_model_registered
from oscar.apps.catalogue.abstract_models import *  # noqa
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.abstract_models import AbstractProduct, AbstractFeature, CustomAbstractCategory, \
    AbstractProductFeature, AbstractProductOptions, AbstractProductImage, CommonFeatureProduct
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import ArrayField
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatPageAdmin
from django.db import IntegrityError
from django.db.models import Min, Q, Prefetch, BooleanField, Case, When, Count, Max
from apps.partner.models import StockRecord

__all__ = ['ProductAttributesContainer']

logger = logging.getLogger(__name__)

if not is_model_registered('catalogue', 'ProductClass'):
    class ProductClass(AbstractProductClass):
        pass

    __all__.append('ProductClass')

if not is_model_registered('catalogue', 'AbstractProductFeature'):
    class ProductFeature(AbstractProductFeature):
        pass

    __all__.append(ProductFeature)

if not is_model_registered('catalogue', 'ProductOptions'):
    class ProductOptions(AbstractProductOptions):
        pass

    __all__.append(ProductOptions)


class ProductiveCategoryQuerySet(models.QuerySet):
    @property
    def parent(self):
        return 'parent'

    @property
    def parent_double(self):
        return '{0}__{0}'.format(self.parent)

    def prefetch(self, children, grandchildren=False):
        prefetch = [Prefetch('children', queryset=children)]

        if grandchildren:
            prefetch += [Prefetch('children__children', queryset=grandchildren)]

        return self.prefetch_related(*prefetch)

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
            'slug', 'name', 'h1', 'meta_title', 'meta_description', 'meta_keywords', 'description',
            'image__file_ptr__file',
            "image__file_ptr__original_filename",
            "image__file_ptr__name",
            "image__is_public",
            'image__id',
            'parent_id',
        )

    def only_page_children(self):
        return self.only(
            'slug', 'name',
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
            children=self.common().select_page().only_page_children(),
            grandchildren=self.common().only_parent()
        ).only_page()


if not is_model_registered('catalogue', 'Category'):
    class Category(CustomAbstractCategory):
        objects = ProductiveCategoryManager()

    __all__.append('Category')


class ProductiveFeatureManager(models.Manager):
    def browse(self):
        return self.get_queryset().select_related('parent').only(
            'title', 'parent'
        ).order_by()

    def simple(self):
        return self.get_queryset().only(
            'id',
        ).order_by()

if not is_model_registered('catalogue', 'Feature'):
    class Feature(AbstractFeature):
        objects = ProductiveFeatureManager()

    __all__.append('Feature')


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

    def only_detail(self):
        return self.only(
            'title',
            'slug',
            'product_class__id',
            'product_class__track_stock',
            'product_class__slug',
            'structure',
            'h1',
            'meta_title',
            'meta_description',
            'meta_keywords',
            'description',
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

    def detail(self):
        return self.list().only_detail()

    def list(self):
        return self.common().select_list().prefetch_list().only_list()

    def promotions(self):
        return self.common().canonical().select_list().prefetch_list().only_list()


if not is_model_registered('catalogue', 'Product'):
    class Product(AbstractProduct):
        objects = ProductiveProductManager()

    __all__.append('Product')


if not is_model_registered('catalogue', 'ProductRecommendation'):
    class ProductRecommendation(AbstractProductRecommendation, CommonFeatureProduct):
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

    __all__.append('ProductRecommendation')


if not is_model_registered('catalogue', 'ProductAttribute'):
    class ProductAttribute(AbstractProductAttribute):
        pass

    __all__.append('ProductAttribute')


if not is_model_registered('catalogue', 'ProductAttributeValue'):
    class ProductAttributeValue(AbstractProductAttributeValue):
        pass

    __all__.append('ProductAttributeValue')


if not is_model_registered('catalogue', 'AttributeOptionGroup'):
    class AttributeOptionGroup(AbstractAttributeOptionGroup):
        pass

    __all__.append('AttributeOptionGroup')


if not is_model_registered('catalogue', 'AttributeOption'):
    class AttributeOption(AbstractAttributeOption):
        pass

    __all__.append('AttributeOption')


if not is_model_registered('catalogue', 'Option'):
    class Option(AbstractOption):
        pass

    __all__.append('Option')


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


if not is_model_registered('catalogue', 'ProductImage'):
    class ProductImage(AbstractProductImage):
        objects = ProductiveProductImageManager()

    __all__.append('ProductImage')


@python_2_unicode_compatible
class SortFeatureInCategory(models.Model):
    feature = models.ForeignKey(Feature, verbose_name=_('Feature'), related_name='sort_from_category')
    category = models.ForeignKey(Category, verbose_name=_('Category'), related_name='sort_from_category')
    sort = models.IntegerField(_('Sort'), default=0, db_index=True)

    class Meta:
        verbose_name = _('Sort feature in category page')
        verbose_name_plural = _('Sorts feature in category page')
        unique_together = ('category', 'feature', 'sort', )

    def __str__(self):
        return u'{}, {} - {}'.format(self.sort, getattr(self, 'category', None), getattr(self, 'feature', None))


from oscar.apps.catalogue.models import *  # noqa
