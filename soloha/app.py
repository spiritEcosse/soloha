from oscar import app
from django.conf.urls import include, url
from oscar.core.loading import get_class, get_model
from dal import autocomplete

detail_view = get_class('catalogue.views', 'ProductDetailView')
catalogue_view = get_class('catalogue.views', 'CatalogueView')
category_view = get_class('catalogue.views', 'ProductCategoryView')
search_view = get_class('search.views', 'FacetedSearchView')
contacts_view = get_class('contacts.views', 'ContactsView')
calculate_price = get_class('catalogue.views', 'ProductCalculatePrice')
Product = get_model('catalogue', 'Product')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class Soloha(app.Shop):
    def get_urls(self):
        urlpatterns = [
            url(r'^search/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)/', search_view.as_view()),
            url(r'^search/', search_view.as_view()),
            url(r'^contacts/', contacts_view.as_view()),
            url(r'^ckeditor/', include('ckeditor_uploader.urls')),
            url(r'^filer/', include('filer.urls')),
            url('^admin/product-autocomplete/$', autocomplete.Select2QuerySetView.as_view(model=Product),
                name='select2_fk'),
            url('^admin/product-recommendation-autocomplete/$', autocomplete.Select2QuerySetView.as_view(model=ProductRecommendation),
                name='product_recommendation_select2_fk'),
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
