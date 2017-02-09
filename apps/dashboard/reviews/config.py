from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ReviewsDashboardConfig(AppConfig):
    label = 'reviews_dashboard'
    name = 'apps.dashboard.reviews'
    verbose_name = _('Reviews dashboard')
