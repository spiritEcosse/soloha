from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VouchersDashboardConfig(AppConfig):
    label = 'vouchers_dashboard'
    name = 'apps.dashboard.vouchers'
    verbose_name = _('Vouchers dashboard')
