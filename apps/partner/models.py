from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from oscar.core.loading import is_model_registered
from apps.partner.abstract_models import AbstractStockRecord
from django.db.models import F

__all__ = []


class ProductiveStockRecordManager(models.Manager):
    def browse(self):
        return self.get_queryset().only(
            'price_excl_tax', 'product', 'price_currency'
        ).order_by('price_excl_tax')


if not is_model_registered('partner', 'StockRecord'):
    class StockRecord(AbstractStockRecord):
        objects = models.Manager()
        productive = ProductiveStockRecordManager()

    __all__.append('StockRecord')


from oscar.apps.partner.models import *  # noqa

markup = models.DecimalField(
    verbose_name=_('Mark-up on goods this partner'), blank=True, decimal_places=2, max_digits=12, default=1
)
markup.contribute_to_class(Partner, "markup")

rate = models.DecimalField(
    verbose_name=_('Rate on goods this partner'), blank=True, decimal_places=2, max_digits=12, default=1
)
rate.contribute_to_class(Partner, "rate")


def save(self, **kwargs):
    super(Partner, self).save(**kwargs)
    StockRecord.objects.filter(
        product__partner=self
    ).update(
        price_excl_tax=F('cost_price') * self.rate * self.markup
    )

Partner.save = save
