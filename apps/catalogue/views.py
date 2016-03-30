from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View
from oscar.core.loading import get_model
from braces import views
from django.views.generic.list import MultipleObjectMixin
from django.db.models.query import Prefetch
import json

Product = get_model('catalogue', 'product')
Category = get_model('catalogue', 'category')


class ProductCategoryView(CoreProductCategoryView):
    pass


class CategoryProducts(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = Product
    paginate_by = 24

    def get_queryset(self, **kwargs):
        queryset = super(CategoryProducts, self).get_queryset().filter(categories=kwargs['category_pk'])
        return queryset.prefetch_related(
            Prefetch('images'),
            Prefetch('categories'),
        ).order_by('-date_created')

    def post(self, request, *args, **kwargs):
        data = json.loads(self.request.body)
        self.kwargs[self.page_kwarg] = data.get('page', 1)
        self.object_list = self.get_queryset(category_pk=data['category_pk'])

    def post_ajax(self, request, *args, **kwargs):
        super(CategoryProducts, self).post_ajax(request, *args, **kwargs)
        return self.render_json_response(self.get_context_data_json())

    def get_paginator_values(self, **kwargs):
        queryset = kwargs.pop('object_list', self.object_list)
        page_size = self.get_paginate_by(queryset)
        paginator_values = {
            'is_paginated': False,
        }

        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            paginator_values = {
                'page_range': paginator.page_range,
                'is_paginated': is_paginated,
                'previous_page_number': page.previous_page_number() if page.has_previous() else None,
                'next_page_number': page.next_page_number() if page.has_next() else None,
                'page_number': page.number,
            }
        return paginator_values

    def get_context_data_json(self, **kwargs):
        context = dict()
        context['products'] = [product.get_values() for product in self.object_list]
        context['paginator'] = self.get_paginator_values()
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

