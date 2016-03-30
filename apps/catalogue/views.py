from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from oscar.core.loading import get_model
from braces import views
from django.views.generic.list import MultipleObjectMixin
from django.db.models.query import Prefetch

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')


class ProductCategoryView(CoreProductCategoryView):
    pass


class CategoryProducts(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = Product
    # paginate_by = 24

    def post(self, request, *args, **kwargs):
        # data = json.loads(self.request.body)
        data = json.loads(self.request.POST)
        self.kwargs[self.sorting_type_kwarg] = data.get('sorting_type', 'stockrecords__price_excl_tax')
        self.object_list = self.get_queryset()
        # self.object_list = self.get_queryset(product_pk=data['product_pk'])

    def get_queryset(self, **kwargs):
        # queryset = super(CategoryProducts, self).get_queryset().filter(products=kwargs['product_pk'])
        queryset = super(CategoryProducts, self).get_queryset()
        return queryset.prefetch_related(
            Prefetch('categories')
        ).order_by('stockrecords__price_excl_tax')
        # ).order_by(kwargs['sorting_type'])

    def post_ajax(self, request, *args, **kwargs):
        super(CategoryProducts, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['products'] = [product.get_values() for product in self.object_list]
        return context

    # def get_paginator_values(self, **kwargs):
    #     queryset = kwargs.pop('object_list', self.object_list)
    #     page_size = self.get_paginate_by(queryset)
    #     paginator_values = {
    #         'is_paginated': False,
    #     }
    #
    #     if page_size:
    #         paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
    #         paginator_values = {
    #             'page_range': paginator.page_range,
    #             'is_paginated': is_paginated,
    #             'previous_page_number': page.previous_page_number() if page.has_previous() else None,
    #             'next_page_number': page.next_page_number() if page.has_next() else None,
    #             'page_number': page.number,
    #         }
    #     return paginator_values


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

