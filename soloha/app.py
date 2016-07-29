from oscar import app
from oscar.core.loading import get_class
from django.conf.urls import url
from apps.flatpages import views

detail_view = get_class('catalogue.views', 'ProductDetailView')
catalogue_view = get_class('catalogue.views', 'CatalogueView')
category_view = get_class('catalogue.views', 'ProductCategoryView')
search_view = get_class('search.views', 'FacetedSearchView')
contacts_view = get_class('contacts.views', 'ContactsView')
sitemap_view = get_class('sitemap.views', 'SitemapView')
subscribe_view = get_class('subscribe.views', 'SubscribeView')


class Soloha(app.Shop):
    def get_urls(self):
        urlpatterns = [
            url(r'^search/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)/', search_view.as_view()),
            url(r'^search/', search_view.as_view()),
            url(r'^contacts/', contacts_view.as_view()),
            url(r'^sitemap/', sitemap_view.as_view()),
            url(r'^subscribe/', subscribe_view.as_view()),
            url(r'^pages/(?P<url>[\w-]+)/$', views.flatpage, name='pages'),
        ]
        urlpatterns += super(Soloha, self).get_urls()
        urlpatterns += [
            # Fallback URL if a not use category slug of the URL
            url(r'^(?P<category_slug>[\w-]+(/(?!filter)[\w-]+(?!filter))*)(?:/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*))*/$', category_view.as_view(), name='category'),
            url(r'^(?P<slug>[\w-]+)$', detail_view.as_view(), name='detail'),
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/(?P<slug>[\w-]+)$', detail_view.as_view(), name='detail'),
            # url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/$', category_view.as_view(), name='category'),
        ]
        return urlpatterns

application = Soloha()
