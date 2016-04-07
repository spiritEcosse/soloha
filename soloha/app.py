from oscar import app
from django.conf.urls import include, url
from oscar.core.loading import get_class

detail_view = get_class('catalogue.views', 'ProductDetailView')
catalogue_view = get_class('catalogue.views', 'CatalogueView')
category_view = get_class('catalogue.views', 'ProductCategoryView')


class Soloha(app.Shop):
    def get_urls(self):
        urlpatterns = super(Soloha, self).get_urls()
        urlpatterns += [
            # Fallback URL if a not use category slug of the URL
            url(r'^(?P<category_slug>[\w-]+(/(?!filter)[\w-]+(?!filter))*)/(filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)/)*$', category_view.as_view(), name='category'),
            url(r'^(?P<slug>[\w-]+)$', detail_view.as_view(), name='detail'),
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/(?P<slug>[\w-]+)$', detail_view.as_view(), name='detail'),
            # url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/$', category_view.as_view(), name='category'),
        ]
        return urlpatterns

application = Soloha()
