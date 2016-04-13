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
from django.db.models import Count
from django.http import HttpResponsePermanentRedirect, Http404
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
import json
import warnings

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
Feature = get_model('catalogue', 'Feature')


class ProductCategoryView(views.JSONResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, generic.ListView):
    template_name = 'catalogue/category.html'
    enforce_paths = True
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def __init__(self, *args, **kwargs):
        super(ProductCategoryView, self).__init__(*args, **kwargs)
        self.products_without_filters = None
        self.object = None
        self.object_list = None

    def post(self, request, *args, **kwargs):
        data = json.loads(self.request.body)
        # self.kwargs['category_slug'] = data.get('category_slug')

        self.kwargs['sorting_type'] = data.get('sorting_type', *Product._meta.ordering)

        self.kwargs['filters'] = data.get('filters', '')
        self.object = self.get_category()
        self.object_list = self.get_queryset()

    def post_ajax(self, request, *args, **kwargs):
        super(ProductCategoryView, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['products'] = [product.get_values() for product in self.object_list]
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_category()
        potential_redirect = self.redirect_if_necessary(
            request.path, self.object)
        if potential_redirect is not None:
            return potential_redirect

        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                                  'price_descending': '-stockrecords__price_excl_tax'}
        self.kwargs['sorting_type'] = dict_new_sorting_types.get(self.request.GET.get('sorting_type'), '-views_count')
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
            expected_path = category.get_absolute_url(self.kwargs)

            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self):
        dict_filter = {'enable': True, 'categories__in': self.object.get_descendants(include_self=True)}
        only = ['title', 'slug', 'structure', 'product_class', 'categories']
        self.products_without_filters = Product.objects.only('id').filter(**dict_filter).distinct().order_by(self.kwargs.get('sorting_type'))

        if self.kwargs.get('filter_slug'):
            dict_filter['filters__slug__in'] = self.kwargs.get('filter_slug').split('/')

        queryset = super(ProductCategoryView, self).get_queryset()
        return queryset.only(*only).filter(**dict_filter).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(self.kwargs['sorting_type'])

    def get_context_data(self, **kwargs):
        # Category.objects.filter(pk=self.object.pk).update(popular=F('popular') + 1)

        context = super(ProductCategoryView, self).get_context_data(**kwargs)

        queryset_filters = Feature.objects.filter(filter_products__in=self.products_without_filters).distinct().prefetch_related('filter_products')
        context['filters'] = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters.annotate(num_prod=Count('filter_products')),
                     to_attr='children_in_products'),
        ).distinct()
        context['filter_slug'] = self.kwargs.get('filter_slug', '')
        context['sort_types'] = []
        sort_types = [('-views_count', _('By popularity'), 'popularity'),
                      ('-stockrecords__price_excl_tax', _('By price descending'), 'price_descending'),
                      ('stockrecords__price_excl_tax', _('By price ascending'), 'price_ascending')]
        for type, text, link in sort_types:
            is_active = False
            if self.kwargs.get('sorting_type', '') == type:
                is_active = True
            sorting_url = '{}?sorting_type={}'.format(self.request.path, link)
            sort_link = 'sorting_type={}'.format(link)
            context['sort_types'].append((sorting_url, text, is_active, sort_link))
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

        attributes = []
        # attributes = AttributeOptionGroup.objects.filter(productattribute__product__parent=self.object).prefetch_related(
        #     Prefetch('options',
        #              queryset=AttributeOption.objects.filter(productattributevalue__product__parent=self.object).distinct(),
        #              to_attr='attribute_value')
        # ).distinct()
        context['attributes'] = attributes

        context['product_options'] = Feature.objects.filter(level=0, children__product_options__product=Product.objects.get(pk=1))

        return context
