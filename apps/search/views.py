from haystack.query import SearchQuerySet

import json
from braces import views
from haystack.views import FacetedSearchView

from django.views import generic
from django.db.models.query import Prefetch
from django.conf import settings
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from apps.search import signals
from apps.catalogue.models import Product, Feature

OSCAR_PRODUCTS_PER_PAGE = getattr(settings, 'OSCAR_PRODUCTS_PER_PAGE', 24)


class CoreFacetedSearchView(FacetedSearchView):
    """
    A modified version of Haystack's FacetedSearchView

    Note that facets are configured when the ``SearchQuerySet`` is initialised.
    This takes place in the search application class.

    See http://django-haystack.readthedocs.org/en/v2.1.0/views_and_forms.html#facetedsearchform # noqa
    """

    # Haystack uses a different class attribute to CBVs
    template = "search/results.html"
    search_signal = signals.user_search

    def __call__(self, request):
        response = super(CoreFacetedSearchView, self).__call__(request)

        # Raise a signal for other apps to hook into for analytics
        self.search_signal.send(
            sender=self, session=self.request.session,
            user=self.request.user, query=self.query)

        return response

    # Override this method to add the spelling suggestion to the context and to
    # convert Haystack's default facet data into a more useful structure so we
    # have to do less work in the template.
    def extra_context(self):
        extra = super(CoreFacetedSearchView, self).extra_context()

        # Show suggestion no matter what.  Haystack 2.1 only shows a suggestion
        # if there are some results, which seems a bit weird to me.
        if self.results.query.backend.include_spelling:
            # Note, this triggers an extra call to the search backend
            suggestion = self.form.get_suggestion()
            if suggestion != self.query:
                extra['suggestion'] = suggestion

        # Convert facet data into a more useful data structure
        if 'fields' in extra['facets']:
            munger = FacetMunger(
                self.request.get_full_path(),
                self.form.selected_multi_facets,
                self.results.facet_counts())
            extra['facet_data'] = munger.facet_data()
            has_facets = any([len(data['results']) for
                              data in extra['facet_data'].values()])
            extra['has_facets'] = has_facets

        # Pass list of selected facets so they can be included in the sorting
        # form.
        extra['selected_facets'] = self.request.GET.getlist('selected_facets')

        return extra

    def get_results(self):
        # We're only interested in products (there might be other content types
        # in the Solr index).
        return super(CoreFacetedSearchView, self).get_results().models(Product)


class FacetedSearchView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreFacetedSearchView, generic.ListView):
    template_name = 'search/results.html'
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.GET.get('q'):
            self.kwargs['search_string'] = self.request.GET.get('q')
            self.kwargs['sorting_type'] = self.request.GET.get('sorting_type', 'popularity')
            self.page_number = request.GET.get('page', '1')
            if self.request.body:
                data = json.loads(self.request.body)
                self.page_number = data.get('page')
            self.kwargs['url'] = self.request.path

        if self.request.body:
            data = json.loads(self.request.body)
            self.kwargs['search_string'] = data.get('search_string', '')

    def post_ajax(self, request, *args, **kwargs):
        super(FacetedSearchView, self).post_ajax(request, *args, **kwargs)
        if self.request.is_ajax() and self.request.GET.get('q'):
            return self.render_json_response(self.get_context_data_json())
        return self.render_json_response(self.get_context_data_live_search_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                                  'price_descending': '-stockrecords__price_excl_tax'}
        self.kwargs['sorting_type'] = dict_new_sorting_types.get(self.kwargs.get('sorting_type', 'popularity'))
        self.products_on_page = self.get_queryset()
        self.paginator = self.get_paginator(self.products_on_page, OSCAR_PRODUCTS_PER_PAGE)
        self.products_current_page = self.paginator.page(self.page_number).object_list
        self.paginated_products = []
        if (int(self.page_number)) != self.paginator.num_pages:
            self.paginated_products = self.paginator.page(str(int(self.page_number) + 1)).object_list

        context['search_string'] = self.kwargs['search_string']
        context['products'] = self.get_product_values(self.products_current_page)
        context['products_next_page'] = self.get_product_values(self.paginated_products)
        context['page_number'] = self.page_number
        context['num_pages'] = self.paginator.num_pages
        context['pages'] = self.get_page_link(self.paginator.page_range)
        context['sorting_type'] = self.kwargs.get('sorting_type')
        return context

    def get_context_data_live_search_json(self, **kwargs):
        context = dict()
        context['searched_products'] = self.get_products()
        context['search_string'] = self.kwargs['search_string']
        return context

    def get(self, request, *args, **kwargs):
        self.kwargs['search_string'] = self.request.GET.get('q')
        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                                      'price_descending': '-stockrecords__price_excl_tax'}

        self.kwargs['sorting_type'] = dict_new_sorting_types.get(self.request.GET.get('sorting_type'), '-views_count')
        self.kwargs['url'] = self.request.path
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
        context['pages'] = self.get_page_link(context['paginator'].page_range)
        for page in context['pages']:
            if page['page_number'] == context['page_obj'].number:
                page['active'] = 'True'
        for type, text, link in sort_types:
            is_active = False
            if self.kwargs.get('sorting_type', '') == type:
                is_active = True
            sorting_url = '{}?q={}&sorting_type={}'.format(self.request.path, context['query'], link)
            sort_link = 'q={}&sorting_type={}'.format(context['query'], link)
            context['sort_types'].append((sorting_url, text, is_active, sort_link))

        return context

    def get_products(self, **kwargs):
        sqs = self.get_search_queryset()[:5]

        searched_products = [{'id': obj.pk,
                              'title': obj.title,
                              'main_image': obj.object.get_values()['image'],
                              'href': obj.object.get_values()['absolute_url'],
                              # 'price': obj.object.get_values()['price']
                              } for obj in sqs]
        return searched_products

    def get_search_queryset(self):
        sqs_search = []
        if self.kwargs['search_string']:
            sqs = SearchQuerySet()
            sqs_title = sqs.autocomplete(title_ngrams=self.kwargs['search_string'])
            sqs_slug = sqs.autocomplete(slug_ngrams=self.kwargs['search_string'])
            sqs_id = sqs.autocomplete(product_id=self.kwargs['search_string'])
            sqs_search = sqs_title or sqs_slug or sqs_id
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

    def get_product_values(self, products):
        values = []

        for product in products:
            product_values = product.get_values()
            product_values['id'] = product.id
            values.append(product_values)

        return values

    def get_page_link(self, page_numbers, **kwargs):
        pages = []

        dict_old_sorting_types = {'-views_count': 'popularity', 'stockrecords__price_excl_tax': 'price_ascending',
                                  '-stockrecords__price_excl_tax': 'price_descending'}

        # this replacement needed, to fix problem with spaces in url
        if self.kwargs['search_string']:
            self.kwargs['search_string'] = self.kwargs['search_string'].replace(' ', '+')

        for page in page_numbers:
            pages_dict = dict()
            pages_dict['page_number'] = page
            pages_dict['link'] = "{}?page={}&q={}&sorting_type={}".format(
                                                                    self.kwargs['url'],
                                                                    page,
                                                                    self.kwargs['search_string'],
                                                                    dict_old_sorting_types.get(self.kwargs.get('sorting_type'), 'popularity'))
            pages_dict['active'] = 'False'
            pages.append(pages_dict)

        return pages
