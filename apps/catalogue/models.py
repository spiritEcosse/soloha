from oscar.core.loading import is_model_registered
from oscar.apps.catalogue.abstract_models import *  # noqa
from apps.catalogue.abstract_models import CustomAbstractProduct, AbstractFeature, CustomAbstractCategory, \
    AbstractProductVersion, AbstractVersionAttribute, AbstractProductFeature, AbstractProductOptions
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import ArrayField
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage

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


class SiteInfo(Site):
    work_time = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    phone_number = models.CharField(max_length=19, blank=True)
    # phone_number = ArrayField(models.CharField(max_length=1000), blank=True)
    email = models.EmailField(max_length=200, blank=True)
    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size': '80'})},
    # }

    class Meta:
        app_label = 'sites'


class InfoPage(FlatPage):
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)

    class Meta:
        app_label = 'flatpages'

    def get_absolute_url(self):
        link = super(InfoPage, self).get_absolute_url()
        return '/{}'.format(link.lstrip('/'))


from oscar.apps.catalogue.models import *  # noqa




