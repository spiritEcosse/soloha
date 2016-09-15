from oscar.core.loading import is_model_registered
from oscar.apps.catalogue.abstract_models import *  # noqa
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.abstract_models import AbstractProduct, AbstractFeature, CustomAbstractCategory, \
    AbstractProductVersion, AbstractVersionAttribute, AbstractProductFeature, AbstractProductOptions, \
    AbstractProductImage, CommonFeatureProduct
from django.contrib.sites.models import Site
from django.contrib.postgres.fields import ArrayField
from django.forms import TextInput
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.admin import FlatPageAdmin
from django.db import IntegrityError


@python_2_unicode_compatible
class StockRecordAttribute(models.Model, CommonFeatureProduct):
    stock_record = models.ForeignKey(
        'partner.StockRecord', verbose_name=_('Stock record of product'), related_name='stock_record_attributes'
    )
    attribute = models.ForeignKey(
        'catalogue.Feature', verbose_name=_('Attribute'), related_name='stock_record_attributes'
    )
    price_retail = models.DecimalField(_("Price (retail)"), decimal_places=2, max_digits=12, blank=True, default=0)
    cost_price = models.DecimalField(_("Cost Price"), decimal_places=2, max_digits=12, blank=True, default=0)

    class Meta:
        unique_together = ('stock_record', 'attribute', )
        app_label = 'catalogue'
        verbose_name = _('StockRecord attribute')
        verbose_name_plural = _('StockRecord attributes')

    def __str__(self):
        return u'{}, {} - {}'.format(self.pk, self.stock_record.product.title, self.attribute.title)

    def save(self, **kwargs):
        stock_records = self.stock_record._meta.model.objects.filter(product=self.stock_record.product)
        search_attributes = (sorted(attr.pk for attr in stock_record.attributes.all()) for stock_record in stock_records)
        current_attributes = list(self.stock_record.attributes.all()) + [self.attribute]
        current_attributes = sorted([attr.pk for attr in current_attributes])

        if current_attributes in search_attributes:
            raise IntegrityError(
                u'UNIQUE constraint failed: catalogue_stockrecord.stockrecord_id, catalogue_stockrecord.attributes '
                u'{} {}'.format(self.stock_record, self.attribute)
            )
        super(StockRecordAttribute, self).save(**kwargs)


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
