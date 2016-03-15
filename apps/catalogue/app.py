from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from apps.catalogue.views import CategoryProducts
from django.conf.urls import url


class CatalogueApplication(CoreCatalogueApplication):
    products = CategoryProducts

    def get_urls(self):
        urls = super(CatalogueApplication, self).get_urls()
        urls += [
            url('^products/', self.products.as_view(), name='products'),
        ]
        return urls

application = CatalogueApplication()
