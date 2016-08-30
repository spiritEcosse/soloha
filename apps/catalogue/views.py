from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import View
from oscar.core.loading import get_model
from braces import views
from django.views.generic.detail import SingleObjectMixin
from django.db.models.query import Prefetch
from django.db.models import Count
from django.http import HttpResponsePermanentRedirect, Http404
from django.utils.http import urlquote
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from django.shortcuts import get_object_or_404
from django.db.models import F
import json
import warnings
from django.db.models import Q
from soloha import settings
from django.db.models import Min, Sum
import operator
import functools
from apps.flatpages.models import InfoPage
from django.http import HttpResponse
import logging
from decimal import Decimal as D
from decimal import ROUND_DOWN
from forms import QuickOrderForm
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import FormView
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader, Context
from easy_thumbnails.files import get_thumbnailer
from django.core.exceptions import ObjectDoesNotExist
from collections import namedtuple
from itertools import groupby
from django.db.models import Count, Case, When, IntegerField
from memoize import memoize, delete_memoized, delete_memoized_verhash
from soloha import settings
from django.core.cache import cache
from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')
ProductVersion = get_model('catalogue', 'ProductVersion')
Feature = get_model('catalogue', 'Feature')
ProductImage = get_model('catalogue', 'ProductImage')
ProductOptions = get_model('catalogue', 'ProductOptions')
ProductFeature = get_model('catalogue', 'ProductFeature')
SiteInfo = get_model('sites', 'Info')
QuickOrder = get_model('order', 'QuickOrder')
WishList = get_model('wishlists', 'WishList')
NOT_SELECTED = str(_('Not selected'))
ANSWER = str(_('Your message has been sent. We will contact you on the specified details.'))


Order = namedtuple('Order', ['title', 'column', 'argument'])


class ProductCategoryView(views.JSONResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, generic.ListView):
    template_name = 'catalogue/category.html'
    enforce_paths = True
    model = Product
    model_single_object = Category
    paginate_by = OSCAR_PRODUCTS_PER_PAGE
    orders = (
        Order(title='By popularity', column='-views_count', argument='popularity'),
        Order(title='By price ascending', column='stockrecords__price_excl_tax', argument='price_ascending'),
        Order(title='By price descending', column='-stockrecords__price_excl_tax', argument='price_descending'),
    )
    use_keys = ('sort', 'filter_slug', )
    feature_only = ('title', 'slug', 'parent__id', 'parent__title', )
    feature_orders = ('parent__sort', 'parent__title',)

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
            return self.render_json_response({})

    def get_context_data_more_goods_json(self, **kwargs):
        context = dict()
        self.object = self.get_object()
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
        self.object = self.get_object(queryset=self.model_single_object.objects.filter(enable=True))
        potential_redirect = self.redirect_if_necessary(request.path, self.object)

        if potential_redirect is not None:
            return potential_redirect

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        self.kwargs['slug'] = self.kwargs['category_slug'].split(Category._slug_separator)[-1]
        obj = super(ProductCategoryView, self).get_object(queryset=queryset)
        filter_slug = self.kwargs.get('filter_slug').split('/') if self.kwargs.get('filter_slug') else []
        self.selected_filters = Feature.objects.only(*self.feature_only).select_related('parent').filter(
            slug__in=filter_slug, level=1
        ).order_by(*self.feature_orders)
        return obj

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            expected_path = category.get_absolute_url(self.kwargs)

            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self, **kwargs):
        sort_argument = self.kwargs.get('sort') or self.orders[0].argument
        sort = filter(lambda order: order.argument == sort_argument, self.orders)[0]

        queryset = super(ProductCategoryView, self).get_queryset()
        queryset = queryset.filter(enable=True, categories=self.object.get_descendants(include_self=True), categories__enable=True)

        selected_filters = list(self.selected_filters)[:]

        if kwargs.get('potential_filter', None):
            selected_filters.append(kwargs.get('potential_filter'))

        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(selected_filters, key=key), key=key)

        for parent, values in iter:
            queryset = queryset.filter(filters__in=map(lambda obj: obj, values))

        queryset = queryset.distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('characteristics'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent'),
        ).order_by(sort.column)
        return queryset

    def get_products(self, **kwargs):
        queryset = Product.objects.filter(
            enable=True, categories=self.object.get_descendants(include_self=True), categories__enable=True
        )

        selected_filters = list(self.selected_filters)[:]

        if kwargs.get('potential_filter', None):
            selected_filters.append(kwargs.get('potential_filter'))

        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(selected_filters, key=key), key=key)

        for parent, values in iter:
            queryset = queryset.filter(filters__in=map(lambda obj: obj, values))

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)

        context['filters'] = Feature.objects.only(*self.feature_only).filter(
            level=1, filter_products__categories=self.object.get_descendants(include_self=True),
            filter_products__enable=True, filter_products__categories__enable=True
        ).order_by(*self.feature_orders).select_related('parent').prefetch_related(
            Prefetch('filter_products')
        ).distinct()

        products = lambda **kwargs: map(lambda obj: obj.id, self.get_products(**kwargs))
        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(self.selected_filters, key=key), key=key)
        filters_parent = map(lambda obj: obj[0], iter)

        for feature in context['filters']:
            feature.potential_products_count = feature.filter_products.filter(
                id__in=products(potential_filter=feature)
            )

            if feature.parent.pk in filters_parent:
                feature.potential_products_count = feature.potential_products_count.exclude(id__in=products)

            feature.potential_products_count = feature.potential_products_count.count()

        context['url_extra_kwargs'] = {key: value for key, value in self.kwargs.items()
                                       if key in self.use_keys and value is not None}
        context['url_extra_kwargs'].update({'category_slug': self.kwargs.get('category_slug')})
        context['page'] = self.kwargs.get('page', None)
        context['orders'] = self.orders
        context['selected_filters'] = self.selected_filters
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


class QuickOrderView(views.JSONResponseMixin, views.AjaxResponseMixin, FormView, SingleObjectMixin):
    form_class = QuickOrderForm
    success_url = reverse_lazy('form_data_valid')
    model = QuickOrder
    template_send_email = 'catalogue/partials/quick_order.html'

    def post(self, request, **kwargs):
        if request.is_ajax():
            return self.ajax(request)
        return super(QuickOrderView, self).post(request, **kwargs)

    def ajax(self, request):
        form = self.form_class(data=json.loads(request.body))
        response_data = {}

        if form.is_valid():
            self.object = form.save(commit=False)

            if not self.request.user.is_anonymous():
                self.object.user = self.request.user
            self.object.save()
            self.send_message()
        else:
            response_data = {'errors': form.errors}

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    def send_message(self):
        current_site = get_current_site(self.request)
        subject = str(_('Order online %s')) % current_site.domain

        from_email = current_site.info.email
        context = {'object': self.object, 'current_site': current_site}

        if self.object.email:
            context_user = context
            context_user = context_user.update({'answer': ANSWER})
            message = loader.get_template(self.template_send_email).render(Context(context_user))
            from_email = self.object.email
            msg = EmailMultiAlternatives(subject, '', current_site.info.email, [self.object.email])
            msg.attach_alternative(message, "text/html")
            msg.send()

        message = loader.get_template(self.template_send_email).render(Context(context))
        msg = EmailMultiAlternatives(subject, '', from_email, [current_site.info.email])
        msg.attach_alternative(message, "text/html")
        msg.send()


class ProductDetailView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreProductDetailView):
    start_option = [{'pk': 0, 'title': NOT_SELECTED}]
    only = ['title', 'pk']

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object
        else:
            self.kwargs['slug'] = self.kwargs['product_slug']
            object = super(ProductDetailView, self).get_object(queryset)
            self.version_first = object.versions.prefetch_related('attributes').order_by('price_retail').first()
            return object

    def redirect_if_necessary(self, current_path, product):
        if self.enforce_paths:
            expected_path = product.get_absolute_url()
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self):
        queryset = super(ProductDetailView, self).get_queryset()
        return queryset.select_related('product_class', 'parent__product_class').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
            Prefetch('images__original'),
            Prefetch('versions'),
            Prefetch('attributes'),
            Prefetch('categories__parent__parent', queryset=Category.objects.only('slug')),
            Prefetch('filters'),
            Prefetch('children__categories__parent__parent'),
            Prefetch('stockrecords__partner'),
            Prefetch('characteristics'),
        )

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
        context['product'] = {'pk': self.object.pk, 'non_standard': self.object.non_standard_price_retail}
        context['product_versions'] = self.get_product_versions()
        context['attributes'] = []
        options_small_thumb = {'size': (30, 30), 'crop': True}

        for attr in self.get_attributes():
            non_standard = attr.features_by_product[0].non_standard if attr.features_by_product else False

            values = self.start_option + [{'pk': value.pk, 'title': value.title, 'parent': attr.pk, 'products': []} for value in attr.values]
            images = []
            selected_val = self.start_option[0]
            selected_val.update({'images': images, 'parent': attr.pk})

            if hasattr(attr, 'selected_val'):
                if getattr(attr.selected_val, 'features_by_product', False):
                    for product in attr.selected_val.features_by_product[0].product_with_images.all()[:5]:
                        images.append({
                            'title': product.get_title(),
                            'pk': product.pk,
                            'thumb_url': get_thumbnailer(product.primary_image()).get_thumbnail(options_small_thumb).url
                        })

                selected_val = {
                    'pk': attr.selected_val.pk,
                    'parent': attr.pk,
                    'products': [],
                    'images': images,
                    'title': attr.selected_val.title
                }

            context['attributes'].append({
                'pk': attr.pk, 'title': attr.title, 'values': values,
                'non_standard': non_standard, 'bottom_line': attr.bottom_line,
                'top_line': attr.top_line,
                'selected_val': selected_val
            })

        context['options'] = [{prod_option.option.pk: prod_option.price_retail} for prod_option in ProductOptions.objects.filter(product=self.object)]
        context['variant_attributes'] = {}

        def get_values(val, tuple_values, attr_pk):
            values = val.get_values(tuple_values)
            values.update({'parent': attr_pk})
            return values

        for attribute in self.get_product_attribute_values():
            attributes = []

            for attr in self.get_attributes_for_attribute(attribute):
                values_in_group = self.start_option + map(lambda val: get_values(val, ('pk', 'title', 'visible'), attr.pk), attr.values_in_group)

                attributes.append({
                    'pk': attr.pk,
                    'title': attr.title,
                    'in_group': values_in_group,
                    'values': values_in_group + map(lambda val: get_values(val, ('pk', 'title'), attr.pk), attr.values_out_group)
                })

            context['variant_attributes'][attribute.pk] = attributes

        product_versions_attributes = {}

        if self.version_first:
            for attr in self.version_first.attributes.all():
                product_versions_attributes[attr.parent.pk] = {'id': attr.pk, 'title': attr.title}
        context['product_version_attributes'] = product_versions_attributes
        context['product_id'] = self.object.id
        if self.get_wish_list():
            context['wish_list_url'] = self.get_wish_list().get_absolute_url()
        context['active'] = self.check_active_product_in_wish_list(wish_list=self.get_wish_list(), product_id=self.object.id)
        return context

    def get_product_attribute_values(self):
        only = ['pk']
        return Feature.objects.only(*only).filter(level=1, product_versions__product=self.object).distinct()

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
        versions = self.object.versions.prefetch_related('attributes').order_by('price_retail')

        for product_version in versions:
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
                if version_attribute.price_retail is not None:
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
        context['product_version_attributes'] = self.version_first
        context['attributes'] = self.get_attributes()
        context['options'] = self.get_options()
        context['not_selected'] = NOT_SELECTED
        context['form'] = QuickOrderForm(initial={'product': self.object.pk})
        context['answer'] = ANSWER
        context['flatpages'] = InfoPage.objects.filter(Q(url='delivery') | Q(url='payment') | Q(url='manager')). \
            filter(enable=True)
        context['pages_delivery_and_pay'] = context['flatpages'].exclude(url='manager')
        context['child'] = self.model.objects.filter(parent__slug=self.object.slug)
        return context

    def get_price(self, context):
        """
        get main price for product
        :param context: get context data
        :return:
            context
        """
        # ToDo make it possible to check whether the product is available for sale
        if not self.version_first:
            selector = Selector()
            strategy = selector.strategy()
            info = strategy.fetch_for_product(self.object)

            if info.availability.is_available_to_buy:
                context['price'] = info.price.incl_tax
                context['currency'] = info.price.currency
            else:
                context['product_not_availability'] = str(_('Product is not available.'))
        else:
            price = self.version_first.price_retail
            for attribute in self.version_first.version_attributes.all():
                if attribute.price_retail is not None:
                    price += attribute.price_retail
            context['price'] = price
            context['currency'] = settings.OSCAR_DEFAULT_CURRENCY
        return context

    def get_attributes(self, filter_attr_val_args=None):
        default_filter_attr_val_args = {'level': 1, 'product_versions__product': self.object}

        if filter_attr_val_args is not None:
            default_filter_attr_val_args.update(filter_attr_val_args)

        attributes = Feature.objects.only(*self.only).filter(
            children__product_versions__product=self.object, level=0
        ).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*self.only).filter(**default_filter_attr_val_args).annotate(
                price=Min('product_versions__price_retail')
            ).prefetch_related(
                Prefetch('product_features', queryset=ProductFeature.objects.filter(product=self.object),
                         to_attr='features_by_product')
            ).order_by('price', 'title', 'pk'), to_attr='values'),
            Prefetch('product_features', queryset=ProductFeature.objects.filter(product=self.object),
                     to_attr='features_by_product')
        ).annotate(
            price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)
        ).order_by('price', '-count_child', 'title', 'pk')

        attributes = sorted(attributes,
                            key=lambda attr: attr.product_features.filter(product=self.object).first().sort
                            if attr.product_features.filter(product=self.object).first() else 0)

        product_versions = self.version_first

        if product_versions:
            target_attributes = set(product_versions.attributes.all())

            for attr in attributes:
                intersection = target_attributes.intersection(set(attr.values))

                if len(intersection) == 1:
                    setattr(attr, 'selected_val', intersection.pop())

        return attributes

    def get_options(self):
        return Feature.objects.filter(Q(level=0), Q(product_options__product=self.object) | Q(children__product_options__product=self.object)).distinct()

    def get_wish_list(self):
        wish_list = WishList.objects.filter(owner=self.request.user.id).first()
        return wish_list

    @staticmethod
    def check_active_product_in_wish_list(wish_list, product_id):
        product_in_wish_list = 'none'
        if wish_list:
            for line in wish_list.lines.all():
                if product_id == line.product_id:
                    product_in_wish_list = 'active'

        return product_in_wish_list


class ProductCalculatePrice(views.JSONRequestResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, View):
    model = Product
    mm = 1000

    def post(self, *args, **kwargs):
        self.object = self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        super(ProductCalculatePrice, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        #ToDo All raise Exception override on ValidationError or similar as angular not working after raise Exception
        context = dict()

        if self.object.non_standard_price_retail != 0:
            data = json.loads(self.request.body)
            custom_features = []
            fields_list = ['pk', 'title', 'parent']
            fields = ' '.join(fields_list)

            current_attr = data['current_attr']

            product_feature = ProductFeature.objects.get(product=self.object, feature=current_attr['parent'])

            context['error'] = {}

            try:
                current_attr['title'] = int(current_attr['title'])
            except ValueError:
                context['error'][current_attr['parent']] = str(_('Please, enter number.'))
            else:
                for val in data['selected_attributes']:
                    custom_feature = namedtuple('CustomFeature', fields)

                    for field in fields_list:
                        setattr(custom_feature, field, int(val.get(field)))
                    custom_features.append(custom_feature)

                count_attr = len(Feature.objects.filter(pk__in=[attr.parent for attr in custom_features], level=0))

                if count_attr != len(custom_features):
                    error = 'Not all passed the attributes exist in the database'
                    logger.error(error)
                    raise Exception(error)

                real_val = [attr.pk for attr in custom_features if attr.pk != -1]
                count_expect_val = len(Feature.objects.filter(pk__in=real_val, level=1))

                if len(real_val) != count_expect_val:
                    error = 'Not all passed the values attributes exist in the database'
                    logger.error(error)
                    raise Exception(error)

                for val in [val for val in custom_features if val.pk == -1]:
                    product_feature = ProductFeature.objects.get(product=self.object, feature=val.parent)

                    if product_feature.non_standard is False:
                        error = 'This attribute "{}" is not available for calculate'.format(product_feature.feature)
                        logger.error(error)
                        raise Exception(error)

                    if val.title < product_feature.feature.bottom_line or val.title > product_feature.feature.top_line:
                        error = str(_('Available size limits: min - "{}", max - "{}"'.
                                      format(product_feature.feature.bottom_line, product_feature.feature.top_line)))
                        context['error'][val.parent] = error

                if not context['error']:
                    calculate_features = map(lambda val: round(float(val.title) / self.mm, 2), custom_features)
                    total_size = functools.reduce(operator.mul, calculate_features, 1)
                    total_size = D(total_size).quantize(D('.01'), rounding=ROUND_DOWN)
                    context['price'] = D(total_size * self.object.non_standard_price_retail).quantize(D('.01'), rounding=ROUND_DOWN)
                    context['error'] = None
        else:
            error = 'Price not available for non-standard'
            logger.error(error)
            raise Exception(error)
        return context


class AttrProd(views.JSONRequestResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, View):
    model = Product

    def post(self, *args, **kwargs):
        self.object = self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        super(AttrProd, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self):
        context = {}
        options_small_thumb = {'size': (30, 30), 'crop': True}
        context['products'] = []
        context['product_primary_images'] = []

        try:
            product_feature = ProductFeature.objects.get(product=self.object, feature=self.kwargs['attr_pk'])
        except ObjectDoesNotExist:
            pass
        else:
            products = product_feature.product_with_images.all()

            for product in products:
                context['products'].append({'title': product.get_title(), 'pk': product.pk, 'images': []})

            for product in products[:5]:
                context['product_primary_images'].append({
                    'title': product.get_title(),
                    'pk': product.pk,
                    'thumb_url': get_thumbnailer(product.primary_image()).get_thumbnail(options_small_thumb).url
                })
        finally:
            return context


class AttrProdImages(views.JSONRequestResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, View):
    model = Product

    def post(self, *args, **kwargs):
        self.object = self.get_object()

    def post_ajax(self, request, *args, **kwargs):
        super(AttrProdImages, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self):
        context = {}
        options = {'size': (400, 400), 'crop': True}
        options_thumb = {'size': (110, 110), 'crop': True}
        context['images'] = []

        for image in self.object.images.all():
            context['images'].append({
                'original_url': get_thumbnailer(image.original).get_thumbnail(options).url,
                'thumb_url': get_thumbnailer(image.original).get_thumbnail(options_thumb).url,
                'caption': image.caption or self.object.get_title(),
            })

        return context
