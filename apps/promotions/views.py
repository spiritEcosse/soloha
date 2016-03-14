from oscar.apps.promotions.views import HomeView as CoreHomeView
from braces import views
from django.views.generic import DetailView, ListView
from oscar.apps.order.models import Line
from apps.catalogue.models import Product
from soloha.settings import MAX_COUNT_PRODUCT
from apps.catalogue.models import ProductRecommendation
from django.utils.html import strip_entities
from sorl.thumbnail import get_thumbnail
from django.db.models.query import Prefetch
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import View
from oscar.core.loading import get_model
from django.views.generic.detail import BaseDetailView
from soloha.settings import IMAGE_NOT_FOUND
from easy_thumbnails.files import get_thumbnailer

Category = get_model('catalogue', 'category')


class HomeView(CoreHomeView):
    template_name = 'promotions/new-homeview.html'

queryset_product = Product.objects.only('title')


class HitsView(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = Line
    template_name = ''

    def get_queryset(self):
        queryset = super(HitsView, self).get_queryset()
        return queryset.prefetch_related(
            Prefetch('product', queryset=queryset_product),
            Prefetch('product__images'),
            Prefetch('product__categories'),
        ).order_by('-product__date_created')[:MAX_COUNT_PRODUCT]

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

    def post_ajax(self, request, *args, **kwargs):
        super(HitsView, self).post_ajax(request, *args, **kwargs)
        products = [line.product.get_values() for line in self.object_list]
        return self.render_json_response(products)


class SpecialView(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    template_name = ''

    def post_ajax(self, request, *args, **kwargs):
        super(SpecialView, self).post_ajax(request, *args, **kwargs)


class RecommendView(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = ProductRecommendation
    template_name = ''

    def get_queryset(self):
        queryset = super(RecommendView, self).get_queryset()
        return queryset.prefetch_related(
            Prefetch('recommendation', queryset=queryset_product),
            Prefetch('recommendation__images'),
            Prefetch('recommendation__categories')
        ).order_by('-recommendation__date_created')[:MAX_COUNT_PRODUCT]

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

    def post_ajax(self, request, *args, **kwargs):
        super(RecommendView, self).post_ajax(request, *args, **kwargs)
        products = [recommend.recommendation.get_values() for recommend in self.object_list]
        return self.render_json_response(products)


class NewView(views.JSONResponseMixin, views.AjaxResponseMixin, MultipleObjectMixin, View):
    model = Product

    def get_queryset(self):
        queryset = super(NewView, self).get_queryset()
        return queryset.prefetch_related(
            Prefetch('images'),
            Prefetch('categories'),
        ).order_by('-date_created').only('title')[:MAX_COUNT_PRODUCT]

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

    def post_ajax(self, request, *args, **kwargs):
        super(NewView, self).post_ajax(request, *args, **kwargs)
        products = [product.get_values() for product in self.object_list]
        return self.render_json_response(products)


class CategoriesView(views.JSONResponseMixin, views.AjaxResponseMixin, View):
    def post(self, request, *args, **kwargs):
        self.object_list = Category.dump_bulk_depth()

    def post_ajax(self, request, *args, **kwargs):
        super(CategoriesView, self).post_ajax(request, *args, **kwargs)
        categories = self.object_list
        return self.render_json_response(categories)
