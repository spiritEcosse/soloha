from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.generic import View
from oscar.core.loading import get_model
from braces import views
from django.views.generic.detail import SingleObjectMixin, ContextMixin
from django.http import HttpResponsePermanentRedirect, HttpResponse, Http404
from django.utils.http import urlquote
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
import json
from django.db.models import Min, Q, Prefetch, BooleanField, Case, When, Count, Max
import operator
import functools
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
from oscar.apps.partner import prices
from oscar.templatetags.currency_filters import currency
from django.utils.functional import cached_property
from django.template.defaultfilters import truncatechars

logger = logging.getLogger(__name__)

Product = get_model('catalogue', 'Product')
StockRecord = get_model('partner', 'StockRecord')
ProductReview = get_model('reviews', 'ProductReview')
Category = get_model('catalogue', 'category')
Feature = get_model('catalogue', 'Feature')
ProductImage = get_model('catalogue', 'ProductImage')
ProductOptions = get_model('catalogue', 'ProductOptions')
ProductFeature = get_model('catalogue', 'ProductFeature')
SiteInfo = get_model('sites', 'Info')
QuickOrder = get_model('order', 'QuickOrder')
WishList = get_model('wishlists', 'WishList')
FlatPage = get_model('flatpages', 'FlatPage')

NOT_SELECTED = unicode(_('Not selected'))
ANSWER = str(_('Your message has been sent. We will contact you on the specified details.'))


Order = namedtuple('Order', ['title', 'column', 'argument'])

TRUNCATECHARS_ATTRIBUTE = 60
TRUNCATECHARS_ATTRIBUTE_TITLE = 15


class Filter(object):
    def filter_feature_parent(self, additional={}):
        filter_product_feature = {}
        lookup_product_feature = 'product'
        product = self.object

        if self.object.is_child:
            product = self.object.parent

        filter_product_feature[lookup_product_feature] = product
        filter_product_feature.update(**additional)
        return filter_product_feature


class BaseCatalogue(ContextMixin):
    url_view_name = 'catalogue:index'
    use_keys = ('sort', )
    orders = (
        Order(title=_('Popularity'), column='-views_count', argument='popularity'),
        Order(title=_('Price ascending'), column='stockrecords__price_excl_tax', argument='price_ascending'),
        Order(title=_('Price descending'), column='stockrecords__price_excl_tax', argument='price_descending'),
    )

    def get_context_data(self, **kwargs):
        context = super(BaseCatalogue, self).get_context_data(**kwargs)
        context['url_view_name'] = self.url_view_name
        context['url_extra_kwargs'] = {key: value for key, value in self.kwargs.items()
                                       if key in self.use_keys and value is not None}
        context['page'] = self.kwargs.get('page', None)
        context['orders'] = self.orders
        return context


class CatalogueView(BaseCatalogue, generic.ListView):
    model = Product
    paginate_by = OSCAR_PRODUCTS_PER_PAGE
    template_name = 'catalogue/browse.html'

    def get_queryset(self, **kwargs):
        sort_argument = self.kwargs.get('sort') or self.orders[0].argument
        sort = filter(lambda order: order.argument == sort_argument, self.orders)[0]

        queryset = super(CatalogueView, self).get_queryset()
        queryset = queryset.filter(enable=True)

        queryset = queryset.distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('characteristics'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent'),
        ).order_by(sort.column)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CatalogueView, self).get_context_data(**kwargs)
        context['summary'] = _("All products")
        return context


class ProductCategoryView(BaseCatalogue, SingleObjectMixin, generic.ListView):
    template_name = 'catalogue/category.html'
    enforce_paths = True
    model = Product
    model_category = Category
    paginate_by = OSCAR_PRODUCTS_PER_PAGE
    use_keys = ('sort', 'filter_slug', )
    feature_only = ('title', 'slug', 'parent__id', 'parent__title', )
    feature_orders = ('parent__sort', 'parent__title',)
    filter_slug = 'filter_slug'
    url_view_name = 'catalogue:category'
    queryset = Product.objects.list()

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

    # @property
    # def object(self):
    #     return self.get_object(queryset=self.model_category.objects.browse_lo_level()
    #         # .prefetch_related(
    #         # Prefetch('children', queryset=Category.objects.browse(level_up=False, fields=['id', 'parent__id']).select_related('parent')),
    #         # Prefetch('children__children', queryset=Category.objects.browse(level_up=False, fields=['id', 'parent__id']).select_related('parent')),
    #     # )
    #     )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=self.model_category.objects.page())
        self.kwargs['filter_slug_objects'] = self.selected_filters
        potential_redirect = self.redirect_if_necessary(request.path, self.object)

        if potential_redirect is not None:
            return potential_redirect

        return super(ProductCategoryView, self).get(request, *args, **kwargs)

    @cached_property
    def selected_filters(self):
        filter_slug = self.kwargs.get(self.filter_slug).split('/') if self.kwargs.get(self.filter_slug) else []
        features = Feature.objects.only(*self.feature_only).select_related('parent').filter(
            slug__in=filter_slug, level=1
        ).order_by('pk')

        if len(filter_slug) != features.count():
            raise Http404('"%s" does not exist' % self.request.get_full_path())

        return features

    def get_object(self, queryset=None):
        self.kwargs['slug'] = self.kwargs['category_slug'].split(self.model_category._slug_separator)[-1]
        return super(ProductCategoryView, self).get_object(queryset=queryset)

    def redirect_if_necessary(self, current_path, category):
        if self.enforce_paths:
            category.page = self.kwargs['page']
            category.order = self.kwargs['sort']
            category.filter_slug_objects = self.kwargs['filter_slug_objects']
            expected_path = category.get_absolute_url

            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self, **kwargs):
        sort_argument = self.kwargs.get('sort') or self.orders[0].argument
        sort = filter(lambda order: order.argument == sort_argument, self.orders)[0]

        queryset = super(ProductCategoryView, self).get_queryset()
        queryset = queryset.filter(
            categories__in=self.object.get_descendants_through_children(),
            categories__enable=True
        )
        selected_filters = list(self.selected_filters)[:]
        key = lambda feature: feature.parent.pk
        iter = groupby(sorted(selected_filters, key=key), key=key)

        for parent, values in iter:
            queryset = queryset.filter(filters__in=map(lambda obj: obj, values))

        queryset = queryset.distinct()

        order = sort.column

        if sort.argument == 'price_ascending' or sort.argument == 'price_descending':
            queryset = queryset.annotate(
                order=Min(sort.column)
            )

            order = 'order' if sort.argument == 'price_ascending' else '-order'

        queryset = queryset.order_by(order)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductCategoryView, self).get_context_data(**kwargs)

        # Todo replace on one query, without regroup
        filters = Feature.objects.browse().only('title', 'parent', 'slug').filter(
            level=1, filter_products__categories__in=self.object.get_descendants_through_children(),
            filter_products__enable=True, filter_products__categories__enable=True
        ).prefetch_related(
            Prefetch(
                'filter_products',
                queryset=Product.objects.filter(id__in=self.get_queryset()).count(),
                to_attr='products'
            )
        ).order_by(*self.feature_orders).distinct()

        for feature in filters:
            print feature
            print type(feature.products)
            print feature.products.count()

        context['filters'] = filters
        context['url_extra_kwargs'].update({'category_slug': self.kwargs.get('category_slug')})
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


class ProductDetailView(views.JSONResponseMixin, views.AjaxResponseMixin, CoreProductDetailView, Filter):
    start_option = [{'pk': 0, 'title': NOT_SELECTED}]
    only = ['title', 'pk']
    lookup_parent = '__parent'

    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object

        self.kwargs['slug'] = self.kwargs['product_slug']
        return super(ProductDetailView, self).get_object(queryset)

    def redirect_if_necessary(self, current_path, product):
        if self.enforce_paths:
            expected_path = product.get_absolute_url
            if expected_path != urlquote(current_path):
                return HttpResponsePermanentRedirect(expected_path)

    def get_queryset(self):
        queryset = super(ProductDetailView, self).get_queryset()
        return queryset.filter(enable=True).select_related('parent__product_class').prefetch_related(
            Prefetch('reviews', queryset=ProductReview.objects.filter(status=ProductReview.APPROVED), to_attr='reviews_approved'),
            Prefetch('options', queryset=Feature.objects.filter(level=0), to_attr='options_enabled'),
            Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
            Prefetch('categories__parent__parent'),
            Prefetch('stockrecords', queryset=StockRecord.objects.order_by('price_excl_tax'),
                     to_attr='stockrecords_list'),
            Prefetch('children__stockrecords', queryset=StockRecord.objects.order_by('price_excl_tax'),
                     to_attr='children_stock_list'),
            'characteristics__parent',
        )
        # .select_related('product_class').prefetch_related(
        # Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
        # Prefetch('images__original'),
        # Prefetch('attributes'),
        # Prefetch('categories__parent__parent'),
        # Prefetch('filters'),
        # Prefetch('reviews'),
        # Prefetch('children__categories__parent__parent'),
        # Prefetch('children__characteristics'),
        # Prefetch('children__images'),
        # Prefetch('stockrecords__partner'),
        # Prefetch('characteristics'),
        # )

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
        context['stockrecords'] = self.get_product_stockrecords()
        context['attributes'] = []
        options_small_thumb = {'size': (30, 30), 'crop': True}

        for attr in self.get_attributes():
            non_standard = attr.features_by_product[0].non_standard if attr.features_by_product else False

            values = self.start_option + [{'pk': value.pk, 'title': value.title, 'parent': attr.pk, 'products': []} for value in attr.values]
            images = []
            selected_val = self.start_option[0]
            selected_val.update({'images': images, 'parent': attr.pk})

            if attr.selected_val:
                selected_val = attr.selected_val[0]

                if selected_val.features_by_product:
                    for product in selected_val.features_by_product[0].product_with_images.all()[:5]:
                        product_image = product.primary_image()
                        images.append({
                            'title': product_image.caption or product.get_title(),
                            'pk': product_image.pk,
                            'thumb_url': get_thumbnailer(product_image.original).get_thumbnail(options_small_thumb).url
                        })

                selected_val = {
                    'pk': selected_val.pk,
                    'parent': attr.pk,
                    'products': [],
                    'images': images,
                    'title': truncatechars(selected_val.title, TRUNCATECHARS_ATTRIBUTE_TITLE)
                }

            context['attributes'].append({
                'pk': attr.pk, 'title': truncatechars(attr.title, TRUNCATECHARS_ATTRIBUTE), 'values': values,
                'non_standard': non_standard, 'bottom_line': attr.bottom_line,
                'top_line': attr.top_line,
                'selected_val': selected_val
            })

        context['options'] = [{prod_option.option.pk: prod_option.price_retail} for prod_option in ProductOptions.objects.filter(product=self.object)]
        context['variant_attributes'] = {}

        # Todo to attempt replace this loop on method values() from django 1.10 which from Prefetch return queryset instead list
        for attribute in self.get_product_attribute_values():
            attributes = []

            for attr in self.get_attributes_for_attribute(attribute):
                values = self.start_option + map(
                    lambda value: value.get_values('pk', 'title', 'visible', 'parent_pk'),
                    attr.values
                )

                attributes.append({
                    'pk': attr.pk,
                    'title': attr.title,
                    'values': values
                })

            context['variant_attributes'][attribute.pk] = attributes

        context['product_id'] = self.object.id

        if self.get_wish_list():
            context['wish_list_url'] = self.get_wish_list().get_absolute_url()

        context['active'] = self.check_active_product_in_wish_list(wish_list=self.get_wish_list(), product_id=self.object.id)
        return context

    def get_product_attribute_values(self):
        only = ['pk']
        return Feature.objects.only(*only).filter(**self.filter_feature_children()).distinct()

    def get_attributes_for_attribute(self, attribute):
        first = StockRecord.objects.filter(
            **self.filter_product_stockrecord()
        ).filter(attributes=attribute).order_by('price_excl_tax').first()

        attributes = Feature.objects.only(*self.only).filter(
            **self.filter_feature()
        ).prefetch_related(
            Prefetch(
                'children',
                queryset=Feature.objects.only(*self.only).filter(
                    **self.filter_feature_children()
                ).annotate(
                    visible=Case(
                        When(pk__in=first.attributes.values_list('id', flat=True), then=True),
                        default=False,
                        output_field=BooleanField()
                    ),
                    price=Min('stockrecords__price_excl_tax')
                ).order_by('-visible', 'price', 'title', 'pk'),
                to_attr='values'
            )
        ).annotate(
            price=Min('children__stockrecords__price_excl_tax'), count_child=Count('children', distinct=True)
        ).order_by('product_features__sort', 'price', '-count_child', 'title', 'pk')

        return attributes

    def get_product_stockrecords(self):
        stockrecord_attributes = dict()
        stockrecords = StockRecord.objects.filter(**self.filter_stockrecord()).order_by()

        for stockrecord in stockrecords:
            attribute_values = stockrecord.attributes.order_by('parent__pk').values_list('pk', flat=True)
            price = prices.FixedPrice(
                currency=stockrecord.price_currency,
                excl_tax=stockrecord.price_excl_tax,
                tax=D('0.00')
            )

            stockrecord_attributes[','.join(map(str, attribute_values))] = {
                'price': currency(price.excl_tax),
                'stockrecord_id': stockrecord.id
            }

        return stockrecord_attributes

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['reviews'] = []
        context['attributes'] = self.get_attributes()
        context['not_selected'] = NOT_SELECTED
        context['form'] = QuickOrderForm(initial={'product': self.object.pk})
        context['answer'] = ANSWER
        context['flatpages'] = FlatPage.objects.select_related('info').filter(
            sites__domain=get_current_site(self.request).domain, info__enable=True
        ).filter(Q(url='delivery') | Q(url='payment') | Q(url='manager'))
        context['pages_delivery_and_pay'] = context['flatpages'].exclude(url='manager')
        context['truncatechars_attribute'] = TRUNCATECHARS_ATTRIBUTE
        context['truncatechars_attribute_title'] = TRUNCATECHARS_ATTRIBUTE_TITLE
        return context

    def filter_stockrecord(self):
        filter_stockrecord = {}
        lookup = 'product'

        if self.object.is_parent:
            lookup += self.lookup_parent

        filter_stockrecord[lookup] = self.object
        return filter_stockrecord

    def filter_stockrecord_attributes(self):
        filter_stockrecord = {}
        lookup = 'attributes__parent__children__stockrecords__product'

        if self.object.is_parent:
            lookup += self.lookup_parent

        filter_stockrecord[lookup] = self.object
        return filter_stockrecord

    def filter_feature_children(self, filter_kwargs=None):
        lookup = 'stockrecords__product'
        filter_children = {'level': 1}

        if self.object.is_parent:
            lookup += self.lookup_parent

        filter_children[lookup] = self.object

        if filter_kwargs is not None:
            filter_children.update(filter_kwargs)

        return filter_children

    def filter_product_feature(self):
        filter_product_feature = {}
        lookup_product_feature = 'product'

        if self.object.is_parent:
            lookup_product_feature += self.lookup_parent

        filter_product_feature[lookup_product_feature] = self.object
        return filter_product_feature

    def filter_feature(self):
        filter_feature = {'level': 0}
        lookup_feature = 'children__stockrecords__product'

        if self.object.is_parent:
            lookup_feature += self.lookup_parent

        filter_feature[lookup_feature] = self.object
        return filter_feature

    def filter_product_stockrecord(self, filter_other={}):
        lookup_feature = 'product'

        if self.object.is_parent:
            lookup_feature += self.lookup_parent

        filter_kw = {lookup_feature: self.object}
        filter_kw.update(filter_other)
        return filter_kw

    def get_attributes(self):
        stockrecord = self.object.get_stockrecord(self.request)

        if stockrecord:
            stockrecord = stockrecord.attributes.prefetch_related(
                Prefetch('product_features', queryset=ProductFeature.objects.filter(
                        **self.filter_feature_parent()
                    ).select_related('product').prefetch_related('product__images__original'), to_attr='features_by_product'
                )
            )

        attributes = Feature.objects.only(*self.only).filter(**self.filter_feature()).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*self.only).filter(
                **self.filter_feature_children()
            ).annotate(
                price=Min('stockrecords__price_excl_tax')
            ).order_by('price', 'title', 'pk'), to_attr='values'),
            Prefetch(
                'children', queryset=stockrecord, to_attr='selected_val'
            ),
            Prefetch('product_features', queryset=ProductFeature.objects.filter(
                    **self.filter_product_feature()
                ).select_related('product').prefetch_related('product__images__original'), to_attr='features_by_product'
            )
        ).annotate(
            price=Min('children__stockrecords__price_excl_tax'), count_child=Count('children', distinct=True)
        ).order_by('product_features__sort', 'price', '-count_child', 'title', 'pk')

        return attributes

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


class AttrProd(views.JSONRequestResponseMixin, views.AjaxResponseMixin, SingleObjectMixin, View, Filter):
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
            product_feature = ProductFeature.objects.get(**self.filter_feature_parent({'feature': self.kwargs['attr_pk']}))
        except ObjectDoesNotExist:
            pass
        else:
            products = product_feature.product_with_images.all().order_by('-date_updated', 'title')

            for product in products:
                context['products'].append({'title': product.get_title(), 'pk': product.pk, 'images': []})

            for product in products[:5]:
                product_image = product.primary_image()
                context['product_primary_images'].append({
                    'title': product.get_title(),
                    'pk': product_image.pk,
                    'thumb_url': get_thumbnailer(product_image.original).get_thumbnail(options_small_thumb).url
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

        for image in self.object.images_all():
            context['images'].append({
                'original_url': get_thumbnailer(image.original).get_thumbnail(options).url,
                'thumb_url': get_thumbnailer(image.original).get_thumbnail(options_thumb).url,
                'caption': image.caption or self.object.get_title(),
                'pk': image.pk,
            })

        return context
