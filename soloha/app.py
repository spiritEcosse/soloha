from oscar import app
from django.conf.urls import include, url
from oscar.core.loading import get_class, get_model
from dal import autocomplete
from apps.catalogue.admin import ProductAutocomplete, FeatureAutocomplete, CategoriesAutocomplete
from apps.partner.admin import PartnerAutocomplete
from oscar.core.loading import get_class
from django.conf.urls import url
from apps.ex_flatpages import views

detail_view = get_class('catalogue.views', 'ProductDetailView')
catalogue_view = get_class('catalogue.views', 'CatalogueView')
category_view = get_class('catalogue.views', 'ProductCategoryView')
search_view = get_class('search.views', 'FacetedSearchView')
contacts_view = get_class('contacts.views', 'ContactsView')
calculate_price = get_class('catalogue.views', 'ProductCalculatePrice')
Product = get_model('catalogue', 'Product')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
sitemap_view = get_class('sitemap.views', 'SitemapView')
subscribe_view = get_class('subscribe.views', 'SubscribeView')


class Soloha(app.Shop):
    def get_urls(self):
        urlpatterns = [
            url(r'^search/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)/', search_view.as_view()),
            url(r'^search/', search_view.as_view()),
            url(r'^contacts/', contacts_view.as_view(), name='contacts'),
            url(r'^ckeditor/', include('ckeditor_uploader.urls')),
            url(r'^filer/', include('filer.urls')),
            url(r'^spirit/product-autocomplete/$', ProductAutocomplete.as_view(), name='product-autocomplete'),
            url(r'^spirit/partner-autocomplete/$', PartnerAutocomplete.as_view(), name='partner-autocomplete'),
            url(r'^spirit/feature-autocomplete/$', FeatureAutocomplete.as_view(), name='feature-autocomplete'),
            url(r'^spirit/categories-autocomplete/$', CategoriesAutocomplete.as_view(), name='categories-autocomplete'),
            url(r'^sitemap/', sitemap_view.as_view()),
            url(r'^subscribe/', subscribe_view.as_view()),
            url(r'^pages/(?P<url>[\w-]+)/$', views.flatpage, name='pages'),
        ]
        urlpatterns += super(Soloha, self).get_urls()
        return urlpatterns

application = Soloha()
