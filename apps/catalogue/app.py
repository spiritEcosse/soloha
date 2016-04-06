from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url


class CatalogueApplication(CoreCatalogueApplication):

    def get_urls(self):
        urls = super(CatalogueApplication, self).get_urls()
        return urls

application = CatalogueApplication()
