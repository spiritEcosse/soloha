from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AnalyticsConfig(AppConfig):
    label = 'analytics'
    name = 'apps.analytics'
    verbose_name = _('Analytics')

    def ready(self):
        from apps.analytics import receivers  # noqa
