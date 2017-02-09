from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ShippingConfig(AppConfig):
    name = 'apps.shipping'
    verbose_name = _('Shipping')
