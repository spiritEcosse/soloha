from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url
from oscar.core.loading import get_class

calculate_price = get_class('catalogue.views', 'ProductCalculatePrice')
quick_order_view = get_class('catalogue.views', 'QuickOrderView')
attr_prod = get_class('catalogue.views', 'AttrProd')
attr_prod_images = get_class('catalogue.views', 'AttrProdImages')


class CatalogueApplication(CoreCatalogueApplication):
    def get_urls(self):
        urlpatterns = super(CatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^calculate/price/(?P<pk>[\d]+)$', calculate_price.as_view(), name='calculate_price'),
            url(r'^quick/order/(?P<pk>[\d]+)$', quick_order_view.as_view(), name='quick_order'),
            url(r'^attr/(?P<attr_pk>[\d]+)/product/(?P<pk>[\d]+)/$', attr_prod.as_view(), name='attr_prod'),
            url(r'^attr/product/(?P<pk>[\d]+)/images/$', attr_prod_images.as_view(), name='attr_prod_images'),
        ]
        return urlpatterns

application = CatalogueApplication()
