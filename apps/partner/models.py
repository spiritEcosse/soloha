from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from oscar.core.loading import is_model_registered
from oscar.apps.partner.abstract_models import (
    AbstractPartner, AbstractStockRecord, AbstractStockAlert)

__all__ = []

if not is_model_registered('partner', 'StockRecord'):
    class StockRecord(AbstractStockRecord):
        product_version = models.ForeignKey(
            'catalogue.ProductVersion', related_name="stockrecords", verbose_name=_("Product version"),
            blank=True, null=True
        )
        product_options = models.ForeignKey(
            'catalogue.ProductOptions', related_name='stockrecords', verbose_name=_('Product options'),
            blank=True, null=True
        )
        plus = models.BooleanField(verbose_name=_('Plus on main price'), default=False)
        percent = models.IntegerField(verbose_name=_('Percent'), null=True, blank=True, default=0)

    __all__.append('StockRecord')


from oscar.apps.partner.models import *  # noqa
