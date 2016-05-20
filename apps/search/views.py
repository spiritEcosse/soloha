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
from django.utils.translation import ugettext_lazy as _
from apps.catalogue.models import Feature
from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Q

Product = get_model('catalogue', 'product')


OSCAR_PRODUCTS_PER_PAGE = getattr(settings, 'OSCAR_PRODUCTS_PER_PAGE', 24)


class FacetedSearchView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreFacetedSearchView, generic.ListView):
    template_name = 'search/results.html'
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.GET.get('q', False):
            return self.get_ajax(request)
        self.kwargs['search_string'] = ''
        if self.request.body:
            data = json.loads(self.request.body)
            self.kwargs['search_string'] = data.get('search_string', '')
        self.products = self.get_products()

    def post_ajax(self, request, *args, **kwargs):
        super(FacetedSearchView, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_ajax(self, request, *args, **kwargs):
        self.kwargs['search_string'] = self.request.GET.get('q')
        self.products = self.get_products()
        # response_data = {'dataa': 'response_data'}
        # return HttpResponse(json.dumps(response_data), content_type="application/json")

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['searched_products'] = self.products
        context['search_string'] = self.kwargs['search_string']
        # context['more_goods'] = self.kwargs.get('more_goods', '')
        return context

    def get(self, request, *args, **kwargs):
        self.kwargs['search_string'] = self.request.GET.get('q')
        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                                      'price_descending': '-stockrecords__price_excl_tax'}

        self.kwargs['sorting_type'] = dict_new_sorting_types.get(self.request.GET.get('sorting_type'), '-views_count')
        # self.kwargs['page'] = self.request.GET.get('page')
        return super(FacetedSearchView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(FacetedSearchView, self).get_context_data(**kwargs)
        context['query'] = self.kwargs['search_string']

        queryset_filters = Feature.objects.filter(filter_products__in=self.products_without_filters).distinct().prefetch_related('filter_products')
        context['filters'] = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters.annotate(num_prod=Count('filter_products')),
                     to_attr='children_in_products'),
        ).distinct()
        context['filter_slug'] = self.kwargs.get('filter_slug', '')

        sort_types = [('-views_count', _('By popularity'), 'popularity'),
                      ('-stockrecords__price_excl_tax', _('By price descending'), 'price_descending'),
                      ('stockrecords__price_excl_tax', _('By price ascending'), 'price_ascending')]
        context['sort_types'] = []
        for type, text, link in sort_types:
            is_active = False
            if self.kwargs.get('sorting_type', '') == type:
                is_active = True
            sorting_url = '{}?q={}&sorting_type={}'.format(self.request.path, context['query'], link)
            sort_link = 'q={}&sorting_type={}'.format(context['query'], link)
            context['sort_types'].append((sorting_url, text, is_active, sort_link))

        # raise Exception(context['paginator'].page(context['page_obj'].next_page_number()).object_list)
        if context['page_obj'].has_next():
            # context['page_obj_next'] = context['paginator'].page(context['page_obj'].next_page_number()).object_list
            context['page_obj_next'] = context['paginator'].page(context['page_obj'].next_page_number())
            context['page_num_next'] = context['page_obj'].next_page_number()

        # self.kwargs['page_obj_next'] = context['page_obj']
        return context

    def get_products(self, **kwargs):
        sqs = self.get_search_queryset()[:5]

        searched_products = [{'id': obj.id,
                              'title': obj.title,
                              'main_image': obj.object.get_values()['image'],
                              'href': obj.object.get_absolute_url(),
                              'price': obj.object.get_values()['price']} for obj in sqs]

        return searched_products

    def get_search_queryset(self):
        sqs_search = []
        if self.kwargs['search_string']:
            sqs = SearchQuerySet()
            sqs_title = sqs.autocomplete(title_ngrams=self.kwargs['search_string'])
            sqs_slug = sqs.autocomplete(slug_ngrams=self.kwargs['search_string'])
            sqs_id = sqs.autocomplete(id_ngrams=self.kwargs['search_string'])
            sqs_search = sqs_title | sqs_slug | sqs_id
        return sqs_search

    def get_queryset(self):
        only = ['title', 'slug', 'structure', 'product_class', 'categories']
        dict_filter = dict()

        products_pk = [product.pk for product in self.get_search_queryset()]
        dict_filter['id__in'] = products_pk
        if self.kwargs.get('filter_slug'):
            dict_filter['filters__slug__in'] = self.kwargs.get('filter_slug').split('/')
        self.products_without_filters = Product.objects.only('id').filter(id__in=products_pk).distinct().order_by(self.kwargs.get('sorting_type'))

        queryset = super(FacetedSearchView, self).get_queryset()
        return queryset.only(*only).filter(**dict_filter).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(self.kwargs['sorting_type'])



