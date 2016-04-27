import json
from braces import views
from django.views import generic
from django.views.generic.detail import SingleObjectMixin
from oscar.apps.search.views import FacetedSearchView as CoreFacetedSearchView
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from oscar.core.loading import get_model
from django.db.models.query import Prefetch
from django.conf import settings

Product = get_model('catalogue', 'product')


OSCAR_PRODUCTS_PER_PAGE = getattr(settings, 'OSCAR_PRODUCTS_PER_PAGE', 24)


class FacetedSearchView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreFacetedSearchView, generic.ListView):
    template_name = 'search/results.html'
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def post(self, request, *args, **kwargs):
        if self.request.body:
            data = json.loads(self.request.body)
            self.kwargs['search_string'] = data.get('search_string', '')
        else:
            self.kwargs['search_string'] = ''
        self.products = self.get_products()

    def post_ajax(self, request, *args, **kwargs):
        super(FacetedSearchView, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['searched_products'] = self.products
        context['search_string'] = self.kwargs['search_string']
        return context

    def get(self, request, *args, **kwargs):
        self.kwargs['search_string'] = self.request.GET.get('q')
        return super(FacetedSearchView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FacetedSearchView, self).get_context_data(**kwargs)
        context['results'] = self.get_search_queryset()
        context['query'] = self.kwargs['search_string']
        return context

    def get_products(self, **kwargs):
        sqs = []
        if self.kwargs['search_string']:
            sqs = self.get_search_queryset()[:5]

        searched_products = [{'id': obj.id,
                              'title': obj.title,
                              'main_image': obj.object.get_values()['image'],
                              'href': obj.object.get_absolute_url(),
                              'price': obj.object.get_values()['price']} for obj in sqs]

        return searched_products

    def get_search_queryset(self):
        return SearchQuerySet().filter(content=AutoQuery(self.kwargs['search_string']))

    def get_queryset(self):
        only = ['title', 'slug', 'structure', 'product_class', 'categories']

        queryset = super(FacetedSearchView, self).get_queryset()
        return queryset.only(*only).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct()


