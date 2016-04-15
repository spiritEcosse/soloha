from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url
from oscar.core.loading import get_class

ProductCRUDView = get_class('catalogue.views', 'ProductCRUDView')
ProductOptionsCRUDView = get_class('catalogue.views', 'ProductOptionsCRUDView')


class CatalogueApplication(CoreCatalogueApplication):

    def get_urls(self):
        urls = super(CatalogueApplication, self).get_urls()
        urls += [
            url(r'^crud/product/?$', ProductCRUDView.as_view(), name='product_crud_view'),
            url(r'^crud/product_options/?$', ProductOptionsCRUDView.as_view(), name='product_options_crud_view'),
        ]
        return urls

application = CatalogueApplication()
