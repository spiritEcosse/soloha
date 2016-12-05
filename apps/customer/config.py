from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CustomerConfig(AppConfig):
    label = 'customer'
    name = 'apps.customer'
    verbose_name = _('Customer')

    def ready(self):
        from apps.customer import receivers  # noqa
        from apps.customer.alerts import receivers  # noqa
