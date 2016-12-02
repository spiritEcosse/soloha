from django.conf.urls import url, include

from soloha.core.application import Application
from apps.catalogue.reviews.app import application as reviews_app
from apps.catalogue import views
from apps.offer.views import RangeDetailView


class BaseCatalogueApplication(Application):
    name = 'catalogue'
    detail_view = views.ProductDetailView
    catalogue_view = views.CatalogueView
    category_view = views.ProductCategoryView
    range_view = RangeDetailView
    product_category_view = views.ProductCategoryView
    calculate_price = views.ProductCalculatePrice
    quick_order_view = views.QuickOrderView
    attr_prod = views.AttrProd
    attr_prod_images = views.AttrProdImages

    def get_urls(self):
        urlpatterns = super(BaseCatalogueApplication, self).get_urls()
        urlpatterns += [
            url(r'^(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$', self.catalogue_view.as_view(), name='index'),
            url(
                r'^category/(?P<category_slug>[\w-]+(/[\w-]+)*)/product/(?P<product_slug>[\w-]+)/$',
                self.detail_view.as_view(), name='detail'
            ),
            url(
                r'^category/(?P<category_slug>[\w-]+(/(?!filter|page|sort)[\w-]+(?!filter|page|sort))*)(?:/filter/(?P<filter_slug>[\w-]+(/(?!page|sort)[\w-]+(?!page|sort))*))*/(?:page/(?P<page>\d+)/)?(?:sort/(?P<sort>[\w-]+)/)?$',
                self.product_category_view.as_view(), name='category'
            ),

            url(r'^ranges/(?P<slug>[\w-]+)/$', self.range_view.as_view(), name='range'),

            url(r'^calculate/price/(?P<pk>[\d]+)$', self.calculate_price.as_view(), name='calculate_price'),
            url(r'^quick/order/(?P<pk>[\d]+)$', self.quick_order_view.as_view(), name='quick_order'),
            url(r'^attr/(?P<attr_pk>[\d]+)/product/(?P<pk>[\d]+)/$', self.attr_prod.as_view(), name='attr_prod'),
            url(r'^attr/product/(?P<pk>[\d]+)/images/$', self.attr_prod_images.as_view(), name='attr_prod_images'),
        ]
        return self.post_process_urls(urlpatterns)


class ReviewsApplication(Application):
    name = None
    reviews_app = reviews_app

    def get_urls(self):
        urlpatterns = super(ReviewsApplication, self).get_urls()
        urlpatterns += [
            url(r'^(?P<product_slug>[\w-]*)_(?P<product_pk>\d+)/reviews/', include(self.reviews_app.urls)),
        ]
        return self.post_process_urls(urlpatterns)


class CatalogueApplication(BaseCatalogueApplication, ReviewsApplication):
    """
    Composite class combining Products with Reviews
    """


application = CatalogueApplication()
