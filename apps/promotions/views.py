from braces import views

from django.db.models.query import Prefetch
from django.views.generic.list import MultipleObjectMixin
from django.views.generic import View
from django.views.generic import TemplateView, RedirectView
from django.core.urlresolvers import reverse

from soloha.settings import MAX_COUNT_PRODUCT

from apps.catalogue.models import Product, Category, ProductRecommendation
from apps.order.models import Line


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
        return queryset.select_related('recommendation').prefetch_related(
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
            Prefetch('categories')
        ).order_by('-date_created')[:MAX_COUNT_PRODUCT]

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


class HomeView(TemplateView):
    """
    This is the home page and will typically live at /
    """
    template_name = 'promotions/home.html'


class RecordClickView(RedirectView):
    """
    Simple RedirectView that helps recording clicks made on promotions
    """
    permanent = False
    model = None

    def get_redirect_url(self, **kwargs):
        try:
            prom = self.model.objects.get(pk=kwargs['pk'])
        except self.model.DoesNotExist:
            return reverse('promotions:home')

        if prom.promotion.has_link:
            prom.record_click()
            return prom.link_url
        return reverse('promotions:home')
