from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import View
from oscar.core.loading import get_model
from braces import views
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.db.models.query import Prefetch
from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
import json
import warnings

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
Filter = get_model('catalogue', 'Filter')


class ProductCategoryView(SingleObjectMixin, generic.ListView):
    template_name = 'catalogue/category.html'
    enforce_paths = True
    model = Category
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, *args, **kwargs):
        super(ProductCategoryView, self).__init__(*args, **kwargs)
        self.products_without_filters = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_category()

        potential_redirect = self.redirect_if_necessary(
            request.path, self.object)
        if potential_redirect is not None:
            return potential_redirect

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def get_category(self):
        if 'pk' in self.kwargs:
            return get_object_or_404(Category, pk=self.kwargs['pk'])
        elif 'category_slug' in self.kwargs:
            concatenated_slugs = self.kwargs['category_slug']
            slugs = concatenated_slugs.split(Category._slug_separator)
            try:
                last_slug = slugs[-1]
            except IndexError:
                raise Http404
            else:
                for category in Category.objects.filter(slug=last_slug):
                    if category.full_slug == concatenated_slugs:
                        message = (
                            "Accessing categories without a primary key"
                            " is deprecated will be removed in Oscar 1.2.")
                        warnings.warn(message, DeprecationWarning)

                        return category

        raise Http404

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            # Categories are fetched by primary key to allow slug changes.
            # If the slug has changed, issue a redirect.
            expected_path = category.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self):
        dict_filter = {'enable': True, 'categories__in': self.object.get_descendants(include_self=True)}
        only = ['title', 'slug', 'structure', 'product_class', 'product_options__name', 'product_options__code',
                'product_options__type', 'enable', 'categories', 'filters']

        self.products_without_filters = Product.objects.only('id').filter(**dict_filter).distinct().order_by(
            self.request.GET.get('sorting_type', *Product._meta.ordering)
        )

        filters = self.request.GET.get('filters')
        if filters:
            dict_filter['filters__slug__in'] = filters.split('/')

        return Product.objects.only(*only).filter(**dict_filter).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_options'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(
            self.request.GET.get('sorting_type', *Product._meta.ordering)
        )

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        # Filter.objects.filter(level=0, children__in=[product.filters.all() for product in self.products])
        # [(filter, filter.parent) for filter in Filter.objects.filter(product__in=)]

        # filters = []
        # for product in self.products_without_filters:
        #     filters.extend(product.filters.all())
        from django.db.models import Count
        context['filters'] = Filter.objects.filter(level=0).prefetch_related(
            Prefetch('children', queryset=Filter.objects.filter(
                products__in=self.products_without_filters
            ).distinct().prefetch_related('products'), to_attr='children_in_products'),
        )
        return context


class CategoryProducts(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    only = ['title', 'slug', 'structure', 'product_class', 'product_options__name', 'product_options__code',
            'product_options__type']

    # TODO check only list and make selecting less fields from stockrecords.

    def post(self, request, *args, **kwargs):
        data = json.loads(self.request.body)
        self.kwargs['product_category'] = data.get('product_category')
        self.kwargs['sorting_type'] = data.get('sorting_type', 'stockrecords__price_excl_tax')
        self.object_list = self.get_queryset()
        # self.object_list = self.get_queryset(product_pk=data['product_pk'])

    def get_queryset(self, **kwargs):
        # queryset = super(CategoryProducts, self).get_queryset().filter(products=kwargs['product_pk'])
        queryset = super(CategoryProducts, self).get_queryset()
        return queryset.only(*self.only).select_related('product_class') \
            .prefetch_related(
            Prefetch('categories'),
            Prefetch('images'),
            Prefetch('stockrecords'),
        ).order_by(self.kwargs['sorting_type'])

    def post_ajax(self, request, *args, **kwargs):
        super(CategoryProducts, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['products'] = [product.get_values() for product in self.object_list]
        return context


class ProductDetailView(CoreProductDetailView):
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(self.object)

        if info.availability.is_available_to_buy:
            context['price'] = info.price.incl_tax
            context['currency'] = info.price.currency
        else:
            context['product_not_availability'] = _('Product is not available.')
        return context

