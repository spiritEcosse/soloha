from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from oscar.core.loading import is_model_registered
from apps.partner.abstract_models import AbstractStockRecord

__all__ = []

if not is_model_registered('partner', 'StockRecord'):
    class StockRecord(AbstractStockRecord):
        pass
    __all__.append('StockRecord')


from oscar.apps.partner.models import *  # noqa
