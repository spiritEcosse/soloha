from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CatalogueConfig(AppConfig):
    label = 'catalogue'
    name = 'apps.catalogue'
    verbose_name = _('Catalogue')

    def ready(self):
        from apps.catalogue import receivers  # noqa
