from django.conf.urls import url, include

from apps.catalogue.views import CatalogueView, ProductDetailView, ProductCategoryView, ProductCalculatePrice, \
    QuickOrderView, AttrProd, AttrProdImages
from apps.offer.views import RangeDetailView


urlpatterns = (
    url(r'^(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$', CatalogueView.as_view(), name='index'),
    url(
        r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/product/(?P<product_slug>[\w-]+)/$',
        ProductDetailView.as_view(), name='detail'
    ),
    url(
        r'^category/(?P<category_slug>[\w-]+(/(?!filter|page|sort)[\w-]+(?!filter|page|sort))*)(?:/filter/(?P<filter_slug>[\w-]+(/(?!page|sort)[\w-]+(?!page|sort))*))*/(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$',
        ProductCategoryView.as_view(), name='category'
    ),
    url(r'^ranges/(?P<slug>[\w-]+)/$', RangeDetailView.as_view(), name='range'),
    url(r'^calculate/price/(?P<pk>[\d]+)$', ProductCalculatePrice.as_view(), name='calculate_price'),
    url(r'^quick/order/(?P<pk>[\d]+)$', QuickOrderView.as_view(), name='quick_order'),
    url(r'^attr/(?P<attr_pk>[\d]+)/product/(?P<pk>[\d]+)/$', AttrProd.as_view(), name='attr_prod'),
    url(r'^attr/product/(?P<pk>[\d]+)/images/$', AttrProdImages.as_view(), name='attr_prod_images'),
    url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/', include('apps.catalogue.reviews.urls')),
)
