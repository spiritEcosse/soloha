from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CheckoutConfig(AppConfig):
    name = 'apps.checkout'
    verbose_name = _('Checkout')
