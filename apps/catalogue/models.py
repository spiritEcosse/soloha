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

if not is_model_registered('catalogue', 'Category'):
    class Category(CustomAbstractCategory):
        pass

    __all__.append('Category')


if not is_model_registered('catalogue', 'Feature'):
    class Feature(AbstractFeature):
        pass

    __all__.append('Filter')


if not is_model_registered('catalogue', 'Product'):
    class Product(AbstractProduct):
        pass

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


if not is_model_registered('catalogue', 'ProductImage'):
    class ProductImage(AbstractProductImage):
        pass

    __all__.append('ProductImage')


from oscar.apps.catalogue.models import *  # noqa
