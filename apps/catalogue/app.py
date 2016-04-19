from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url
from oscar.core.loading import get_class


class CatalogueApplication(CoreCatalogueApplication):

    def get_urls(self):
        return super(CatalogueApplication, self).get_urls()

application = CatalogueApplication()
