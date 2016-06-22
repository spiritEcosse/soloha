from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url
from oscar.core.loading import get_class

calculate_price = get_class('catalogue.views', 'ProductCalculatePrice')
quick_order_view = get_class('catalogue.views', 'QuickOrderView')


class CatalogueApplication(CoreCatalogueApplication):
    def get_urls(self):
        urlpatterns = super(CatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^calculate/price/(?P<pk>[\d]+)$', calculate_price.as_view(), name='calculate_price'),
            url(r'^quick/order/(?P<pk>[\d]+)$', quick_order_view.as_view(), name='quick_order'),
        ]
        return urlpatterns

application = CatalogueApplication()
