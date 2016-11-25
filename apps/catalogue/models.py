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
    def prefetch(self, queryset):
        return self.prefetch_related(
            Prefetch('children', queryset=queryset),
            Prefetch('children__children', queryset=queryset),
        )

    def select_main_menu(self):
        return self.select_related('image_banner', 'icon')

    def included(self):
        return self.filter(enable=True)

    def menu_only(self):
        return self.only(
            'slug',
            'name',
            'parent__id',
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

    def lo_only(self):
        return self.only('slug', 'name', 'parent__id')

    def only_simple(self):
        return self.only('id')

    def order(self):
        return self.order_by()

    def page_only(self):
        return self.only(
            'slug', 'name', 'h1', 'slug', 'meta_title', 'meta_description', 'meta_keywords', 'description',
            'image__file_ptr__file',
            "image__file_ptr__original_filename",
            "image__file_ptr__name",
            "image__is_public",
            'image__id',
        )

    def select_product_url(self):
        return self.select_related('parent__parent')

    def select_page(self):
        return self.select_related('image')


class ProductiveCategoryManager(models.Manager):
    def get_queryset(self):
        return ProductiveCategoryQuerySet(self.model, using=self._db)

    def common(self):
        return self.get_queryset().included().only_simple().order()

    def menu(self):
        return self.common().select_main_menu().prefetch(queryset=self.lo()).menu_only()

    def lo(self):
        return self.common().lo_only()

    def page(self):
        return self.common().select_product_url().prefetch(queryset=self.common()).page_only()


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


class ProductiveProductManager(models.Manager):
    def prefetch(self):
        return self.select_related('product_class').prefetch_related(
            Prefetch('categories', queryset=Category.objects.browse_lo_level().select_related('parent__parent')),
            Prefetch('stockrecords', queryset=StockRecord.objects.browse()),
            Prefetch('characteristics', queryset=Feature.objects.browse()),
            Prefetch('images', queryset=ProductImage.objects.browse()),
            Prefetch('children', queryset=Product.objects.select_related('parent').only('id', 'parent').order_by(
                'stockrecords__{}'.format(StockRecord.order_by_price()))),
            Prefetch('children__stockrecords', queryset=StockRecord.objects.browse()),
        ).only(
            'title',
            'slug',
            'product_class__id',
            'product_class__track_stock',
            'product_class__slug',
            'structure',
            'upc',
        ).order_by()

    def browse(self):
        return self.prefetch().filter(enable=True, parent=None)

    def browse_all(self):
        return self.prefetch().filter(enable=True)


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


from oscar.apps.catalogue.models import *  # noqa
