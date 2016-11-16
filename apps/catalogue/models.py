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


def only():
    return [
        'slug',
        'name',
        'parent',
        'icon__file_ptr__file',
        "icon__file_ptr__original_filename",
        "icon__file_ptr__name",
        "icon__is_public",
        'image_banner__file_ptr__file',
        "image_banner__file_ptr__original_filename",
        "image_banner__file_ptr__name",
        "image_banner__is_public",
        'image_banner',
        'link_banner'
    ]


class ProductiveCategoryManager(models.Manager):
    def prefetch(self):
        return self.get_queryset().select_related('image_banner', 'icon').prefetch_related(
            Prefetch('children', queryset=Category.productive.browse_lo_level()),
            Prefetch('children__children', queryset=Category.productive.browse_lo_level()),
        )

    def browse(self, level_up=True, fields=only()):
        lookup = {'enable': True}
        queryset = self.get_queryset()

        if level_up:
            lookup['level'] = 0
            queryset = self.prefetch()

        queryset = queryset.filter(**lookup)
        return queryset.only(*fields)

    def browse_lo_level(self):
        return self.browse(level_up=False, fields=['slug', 'name', 'parent'])


if not is_model_registered('catalogue', 'Category'):
    class Category(CustomAbstractCategory):
        objects = models.Manager()
        productive = ProductiveCategoryManager()

    __all__.append('Category')


class ProductiveFeatureManager(models.Manager):
    def browse(self):
        return self.get_queryset().select_related('parent').only(
            'title', 'parent'
        ).order_by('sort')

if not is_model_registered('catalogue', 'Feature'):
    class Feature(AbstractFeature):
        productive = ProductiveFeatureManager()
        objects = models.Manager()

    __all__.append('Filter')


class ProductiveProductManager(models.Manager):
    def prefetch(self):
        return self.select_related('product_class').prefetch_related(
            Prefetch('categories', queryset=Category.productive.browse_lo_level().select_related('parent__parent')),
            'children',
            Prefetch('stockrecords', queryset=StockRecord.productive.browse()),
            Prefetch('characteristics', queryset=Feature.productive.browse()),
            Prefetch('images', queryset=ProductImage.productive.browse()),
        ).only(
            'title',
            'slug',
            'product_class',
            'structure',
            'upc',
        )

    def browse(self):
        return self.prefetch().filter(enable=True, parent=None)

    def browse_with_children(self):
        return self.prefetch().filter(enable=True)


if not is_model_registered('catalogue', 'Product'):
    class Product(AbstractProduct):
        productive = ProductiveProductManager()

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
            'original__file_ptr__file',
            "original__is_public",
            'product',
        ).order_by('display_order')


if not is_model_registered('catalogue', 'ProductImage'):
    class ProductImage(AbstractProductImage):
        productive = ProductiveProductImageManager()
        objects = models.Manager()

    __all__.append('ProductImage')


from oscar.apps.catalogue.models import *  # noqa
