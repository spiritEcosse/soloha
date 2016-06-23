from oscar.core.loading import is_model_registered
from oscar.apps.catalogue.abstract_models import *  # noqa
from apps.catalogue.abstract_models import CustomAbstractProduct, AbstractFeature, CustomAbstractCategory, \
    AbstractProductVersion, AbstractVersionAttribute, AbstractProductFeature, AbstractProductOptions, AbstractQuickOrder
from django.contrib.sites.models import Site
from apps.catalogue.abstract_models import REGEXP_PHONE
from django.contrib.postgres.fields import ArrayField
from django.forms import TextInput

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

if not is_model_registered('catalogue', 'ProductVersion'):
    class ProductVersion(AbstractProductVersion):
        pass

    __all__.append(ProductVersion)

if not is_model_registered('catalogue', 'VersionAttribute'):
    class VersionAttribute(AbstractVersionAttribute):
        pass

    __all__.append('VersionAttribute')

if not is_model_registered('catalogue', 'Category'):
    class Category(CustomAbstractCategory):
        pass

    __all__.append('Category')


if not is_model_registered('catalogue', 'Feature'):
    class Feature(AbstractFeature):
        pass

    __all__.append('Filter')


if not is_model_registered('catalogue', 'Product'):
    class Product(CustomAbstractProduct):
        pass

    __all__.append('Product')


if not is_model_registered('catalogue', 'ProductRecommendation'):
    class ProductRecommendation(AbstractProductRecommendation):
        pass

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


if not is_model_registered('catalogue', 'QuickOrder'):
    class QuickOrder(AbstractQuickOrder):
        pass

    __all__.append('QuickOrder')

# if not is_model_registered('catalogue', 'SiteInfo'):
@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    work_time = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    phone_number = models.CharField(max_length=19, blank=True)
    # phone_number = ArrayField(models.CharField(max_length=1000), blank=True)
    email = models.EmailField(max_length=200)
    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size': '80'})},
    # }

    def __str__(self):
        return self.site.domain

    class Meta:
        app_label = 'sites'


from oscar.apps.catalogue.models import *  # noqa




