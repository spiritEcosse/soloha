from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.shortcuts import render_to_response
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
from django.core import serializers
from djangular.views.crud import NgCRUDView
from oscar.core.loading import get_class
from django.db.models import Q
from soloha import settings
from django.db.models import Min, Sum

from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery
from django.template import defaultfilters
from django.http import HttpResponse

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
ProductVersion = get_model('catalogue', 'ProductVersion')
Feature = get_model('catalogue', 'Feature')
ProductOptions = get_model('catalogue', 'ProductOptions')

NOT_SELECTED = str(_('Not selected'))


class ProductCategoryView(views.JSONResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, generic.ListView):
    template_name = 'catalogue/category.html'
    enforce_paths = True
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            if self.request.body:
                data = json.loads(self.request.body)
                self.page_number = data.get('page')
                self.kwargs['sorting_type'] = data.get('sorting_type')
            self.kwargs['url'] = self.request.path

    def post_ajax(self, request, *args, **kwargs):
        super(ProductCategoryView, self).post_ajax(request, *args, **kwargs)
        if self.request.is_ajax():
            return self.render_json_response(self.get_context_data_more_goods_json())

    def get_context_data_more_goods_json(self, **kwargs):
        context = dict()
        self.object = self.get_category()
        self.products_on_page = self.get_queryset()

        self.paginator = self.get_paginator(self.products_on_page, OSCAR_PRODUCTS_PER_PAGE)
        self.products_current_page = self.paginator.page(self.page_number).object_list
        self.paginated_products = []
        if (int(self.page_number)) != self.paginator.num_pages:
            self.paginated_products = self.paginator.page(str(int(self.page_number) + 1)).object_list

        context['products'] = self.get_product_values(self.products_current_page)
        context['products_next_page'] = self.get_product_values(self.paginated_products)
        context['page_number'] = self.page_number
        context['num_pages'] = self.paginator.num_pages
        context['pages'] = self.get_page_link(self.paginator.page_range)
        context['sorting_type'] = self.kwargs['sorting_type']
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

        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                              'price_descending': '-stockrecords__price_excl_tax'}
        self.kwargs['sorting_type'] = dict_new_sorting_types.get(self.kwargs.get('sorting_type'), self.kwargs.get('sorting_type', '-views_count'))

        self.products_without_filters = Product.objects.only('id').filter(**dict_filter).distinct().order_by(self.kwargs.get('sorting_type'))

        if self.kwargs.get('filter_slug'):
            dict_filter['filters__slug__in'] = self.kwargs.get('filter_slug').split('/')

        queryset = super(ProductCategoryView, self).get_queryset()
        queryset = queryset.only(*only).filter(**dict_filter).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(self.kwargs['sorting_type'])
        return queryset

    def get_context_data(self, **kwargs):
        # Category.objects.filter(pk=self.object.pk).update(popular=F('popular') + 1)

        context = super(ProductCategoryView, self).get_context_data(**kwargs)
        queryset_filters = Feature.objects.filter(filter_products__in=self.products_without_filters).distinct().prefetch_related('filter_products')
        context['filters'] = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters.annotate(num_prod=Count('filter_products')),
                     to_attr='children_in_products'),).distinct()
        context['filter_slug'] = self.kwargs.get('filter_slug', '')
        # this for more goods
        self.kwargs['url'] = self.request.path
        context['pages'] = self.get_page_link(context['paginator'].page_range)
        for page in context['pages']:
            if page['page_number'] == context['page_obj'].number:
                page['active'] = 'True'
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

    def get_page_link(self, page_numbers, **kwargs):
        pages = []

        dict_old_sorting_types = {'-views_count': 'popularity', 'stockrecords__price_excl_tax': 'price_ascending',
                                  '-stockrecords__price_excl_tax': 'price_descending'}

        for page in page_numbers:
            pages_dict = dict()
            pages_dict['page_number'] = page
            pages_dict['link'] = "{}?page={}&sorting_type={}".format(
                                                                    self.kwargs['url'],
                                                                    page,
                                                                    dict_old_sorting_types.get(self.kwargs.get('sorting_type'), 'popularity'))
            pages_dict['active'] = 'False'
            pages.append(pages_dict)

        return pages

    def get_product_values(self, products):
        values = []
        for product in products:
            product_values = product.get_values()
            product_values['id'] = product.id
            values.append(product_values)

        return values


class ProductDetailView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreProductDetailView):
    start_option = [{'pk': 0, 'title': NOT_SELECTED}]
    only = ['title', 'pk']

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.body:
            data = json.loads(self.request.body)
            self.kwargs['option_id'] = data.get('option_id')
            self.kwargs['parent'] = data.get('parent', None)
            self.kwargs['list_options'] = data.get('list_options', '')
        else:
            self.kwargs['option_id'] = None
            self.kwargs['parent'] = None

    def post_ajax(self, request, *args, **kwargs):
        super(ProductDetailView, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['product_versions'] = self.get_product_versions()
        context['attributes'] = []

        for attr in self.get_attributes():
            values = self.start_option + [{'pk': value.pk, 'title': value.title} for value in attr.values]
            context['attributes'].append({'pk': attr.pk, 'title': attr.title, 'values': values})

        context['options'] = [{prod_option.option.pk: prod_option.price_retail} for prod_option in ProductOptions.objects.filter(product=self.object)]
        self.get_price(context)
        context['not_selected'] = NOT_SELECTED
        context['variant_attributes'] = {}

        def get_values_in_group(value):
            data = value.get_values(('pk', 'title'))
            data.update({'group': str(_('in_group')), 'first_visible': value.visible})
            return data

        def get_values_out_group(value):
            data = value.get_values(('pk', 'title'))
            data.update({'group': str(_('out_group'))})
            return data

        for attribute in self.get_product_attribute_values():
            attributes = []

            for attr in self.get_attributes_for_attribute(attribute):
                values_in_group = self.start_option + map(get_values_in_group, attr.values_in_group)

                attributes.append({
                    'pk': attr.pk,
                    'title': attr.title,
                    'in_group': values_in_group,
                    'values': values_in_group + map(get_values_out_group, attr.values_out_group),
                })

            context['variant_attributes'][attribute.pk] = attributes

        product_versions_attributes = {}
        product_versions = self.product_versions_queryset().first()

        if product_versions:
            for attr in product_versions.attributes.all():
                product_versions_attributes[attr.parent.pk] = {'pk': attr.pk, 'title': attr.title}
        context['product_version_attributes'] = product_versions_attributes
        return context

    def product_versions_queryset(self):
        # ToDo igor: add to order_by - 'parent__product_features__sort'
        return ProductVersion.objects.filter(product=self.object).prefetch_related('attributes').order_by('price_retail')

    def get_product_attribute_values(self):
        only = ['pk']
        return Feature.objects.only(*only).filter(level=1, product_versions__product=self.object).distinct().order_by()

    def get_attributes_for_attribute(self, attribute):
        values_in_group = Feature.objects.only(*self.only).filter(
            level=1, product_versions__product=self.object, product_versions__attributes=attribute
        )

        attributes = Feature.objects.only(*self.only).filter(
            children__product_versions__product=self.object, level=0
        ).prefetch_related(
            Prefetch('children', queryset=values_in_group.annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values_in_group'),
            Prefetch('children', queryset=Feature.objects.only(*self.only).filter(
                level=1, product_versions__product=self.object
            ).exclude(
                version_attributes__attribute__in=values_in_group.order_by().distinct()
            ).annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values_out_group')
        ).annotate(
            price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)
        ).order_by('price', '-count_child', 'title', 'pk')

        first = ProductVersion.objects.filter(product=self.object).annotate(
            price_common=Sum('version_attributes__price_retail') + F('price_retail')
        ).filter(attributes=attribute).order_by('price_common').first()

        attributes = sorted(attributes,
                            key=lambda attr: attr.product_features.filter(product=self.object).first().sort
                            if attr.product_features.filter(product=self.object).first() else 0)

        for attr in attributes:
            for val in attr.values_in_group:
                val.prices = []
                val.visible = val in first.attributes.all()

                for prod_ver in val.product_versions.filter(attributes=val, product=self.object).filter(attributes=attribute):
                    price = ProductVersion.objects.filter(pk=prod_ver.pk).aggregate(
                        common=Sum('version_attributes__price_retail'))
                    price['common'] += prod_ver.price_retail
                    val.prices.append(price['common'])
            attr.values_in_group = sorted(attr.values_in_group, key=lambda val: min(val.prices))

        return attributes

    def get_product_versions(self):
        product_versions = dict()

        for product_version in self.product_versions_queryset():
            attribute_values = []
            price = product_version.price_retail
            version_attributes = product_version.version_attributes.filter(
                attribute__parent__children__product_versions__product=self.object, attribute__level=1,
                attribute__parent__level=0
            ).annotate(
                price=Min('version__price_retail'),
                count_child=Count('attribute__parent__children', distinct=True)
            ).order_by('price', '-count_child', 'attribute__parent__title', 'attribute__parent__pk')
            for version_attribute in version_attributes:
                attribute_values.append(version_attribute.attribute)
                if version_attribute.plus and version_attribute.price_retail is not None:
                    price += version_attribute.price_retail
            attribute_values = sorted(attribute_values,
                                      key=lambda attr: attr.product_features.filter(
                                          product=self.object).first().sort
                                      if attr.product_features.filter(product=self.object).first() else 0)
            attribute_values = [str(val.pk) for val in attribute_values]
            product_versions[','.join(attribute_values)] = str(price)
        return product_versions

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)

        self.get_price(context)
        context['product_version_attributes'] = self.product_versions_queryset().first()
        context['attributes'] = self.get_attributes()
        context['options'] = self.get_options()
        context['not_selected'] = NOT_SELECTED
        return context

    def get_price(self, context):
        """
        get main price for product
        :param context: get context data
        :return:
            context
        """
        first_prod_version = self.product_versions_queryset().first()

        # ToDo make it possible to check whether the product is available for sale
        if not first_prod_version:
            selector = Selector()
            strategy = selector.strategy()
            info = strategy.fetch_for_product(self.object)

            if info.availability.is_available_to_buy:
                context['price'] = info.price.incl_tax
                context['currency'] = info.price.currency
            else:
                context['product_not_availability'] = str(_('Product is not available.'))
        else:
            price = first_prod_version.price_retail
            for attribute in first_prod_version.version_attributes.all():
                if attribute.plus:
                    price += attribute.price_retail
            context['price'] = price
            context['currency'] = settings.OSCAR_DEFAULT_CURRENCY
        return context

    def get_attributes(self, filter_attr_val_args=None):
        only = ['title', 'pk']
        default_filter_attr_val_args = {'level': 1, 'product_versions__product': self.object}

        if filter_attr_val_args is not None:
            default_filter_attr_val_args.update(filter_attr_val_args)

        attributes = Feature.objects.only(*only).filter(
            children__product_versions__product=self.object, level=0
        ).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*only).filter(**default_filter_attr_val_args).annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values')
        ).annotate(
            price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)
        ).order_by('price', '-count_child', 'title', 'pk')

        attributes = sorted(attributes,
                            key=lambda attr: attr.product_features.filter(product=self.object).first().sort
                            if attr.product_features.filter(product=self.object).first() else 0)
        return attributes

    def get_options(self):
        return Feature.objects.filter(Q(level=0), Q(product_options__product=self.object) | Q(children__product_options__product=self.object)).distinct()

