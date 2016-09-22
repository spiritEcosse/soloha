from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication
from django.views.generic.list import MultipleObjectMixin
from django.conf.urls import url
from oscar.core.loading import get_class, get_model
from django.views.decorators.cache import cache_page


class CatalogueApplication(CoreCatalogueApplication):
    product_category_view = get_class('catalogue.views', 'ProductCategoryView')
    calculate_price = get_class('catalogue.views', 'ProductCalculatePrice')
    quick_order_view = get_class('catalogue.views', 'QuickOrderView')
    attr_prod = get_class('catalogue.views', 'AttrProd')
    attr_prod_images = get_class('catalogue.views', 'AttrProdImages')

    def get_urls(self):
        urlpatterns = [
            url(r'^(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$', self.catalogue_view.as_view(), name='index'),
            url(r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/product/(?P<product_slug>[\w-]+)/$', self.detail_view.as_view(), name='detail'),
            url(r'^category/(?P<category_slug>[\w-]+(/(?!filter|page|sort)[\w-]+(?!filter|page|sort))*)(?:/filter/(?P<filter_slug>[\w-]+(/(?!page|sort)[\w-]+(?!page|sort))*))*/(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$',
                self.product_category_view.as_view(), name='category'),
        ]
        urlpatterns += super(CatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^calculate/price/(?P<pk>[\d]+)$', self.calculate_price.as_view(), name='calculate_price'),
            url(r'^quick/order/(?P<pk>[\d]+)$', self.quick_order_view.as_view(), name='quick_order'),
            url(r'^attr/(?P<attr_pk>[\d]+)/product/(?P<pk>[\d]+)/$', self.attr_prod.as_view(), name='attr_prod'),
            url(r'^attr/product/(?P<pk>[\d]+)/images/$', self.attr_prod_images.as_view(), name='attr_prod_images'),
        ]
        return urlpatterns

application = CatalogueApplication()
