from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from oscar.test import factories
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
import json
from django.db.models.query import Prefetch
from oscar.core.loading import get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from test.factories import catalogue
from apps.promotions.views import HomeView

Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
Line = get_model('order', 'Line')
test_catalogue = catalogue.Test()


class TestHomePage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        """
        test home page, test this models: Category, Product, ProductRecommendation, Line.
        Returns:
            None
        """
        test_catalogue.create_product_bulk_recommend()
        test_catalogue.create_order()
        with self.assertNumQueries(28):
            response = self.client.get(reverse('promotions:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, HomeView.as_view().__name__)
        self.assertEqual(response.resolver_match.view_name, 'promotions:home')
        self.assertTemplateUsed(response, 'promotions/home.html')

        only = ['title', 'slug', 'structure', 'product_class', 'product_options__name', 'product_options__code', 'product_options__type', 'categories']

        products_queryset = Product.objects.only(*only).select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_options'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).order_by('-date_created')[:MAX_COUNT_PRODUCT]
        self.assertEqual(str(products_queryset.query), str(response.context['products_new'].query))
        products_expected = [product.get_values() for product in products_queryset]

        with self.assertNumQueries(0):
            products_news = [product.get_values() for product in response.context['products_new']]
        self.assertListEqual(products_news, products_expected)

        products_queryset = Product.objects.only(*only).filter(productrecommendation__isnull=False).select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_options'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).order_by('-date_created')[:MAX_COUNT_PRODUCT]
        self.assertEqual(str(products_queryset.query), str(response.context['products_recommend'].query))
        products_expected = [product.get_values() for product in products_queryset]

        with self.assertNumQueries(0):
            products_recommend = [product.get_values() for product in response.context['products_recommend']]
        self.assertListEqual(products_recommend, products_expected)

        products_queryset = Product.objects.only(*only).filter(line__isnull=False).select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_options'),
            Prefetch('stockrecords'),
            Prefetch('product_class__options'),
            Prefetch('categories__parent__parent'),
        ).order_by('-date_created')[:MAX_COUNT_PRODUCT]
        self.assertEqual(str(products_queryset.query), str(response.context['products_order'].query))
        products_expected = [product.get_values() for product in products_queryset]

        with self.assertNumQueries(0):
            products_order = [product.get_values() for product in response.context['products_order']]
        self.assertListEqual(products_order, products_expected)

        test_catalogue.test_menu_categories(obj=self, response=response)

    # def test_categories_menu(self):
    #     """
    #     test main menu with categories
    #     Returns:
    #         None
    #     """
    #     self.create_category()
    #     with self.assertNumQueries(3):
    #         response = self.client.post(reverse('promotions:categories'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     categories = Category.dump_bulk_depth(max_depth=3)
    #     self.assertJSONEqual(json.dumps(categories), response.content)
    #
    #
    # def test_hits_product(self):
    #     """
    #     test bestsellers products
    #     Returns:
    #         None
    #     """
    #     factories.create_order()
    #     response = self.client.post(reverse('promotions:hits'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(200, response.status_code)
    #     products = [line.product.get_values() for line in Line.objects.order_by('-product__date_created')[:MAX_COUNT_PRODUCT]]
    #     self.assertJSONEqual(json.dumps(products), response.content)
    #
    # def create_category(self):
    #     """
    #     create bulk category
    #     Returns:
    #         None
    #     """
    #     categories = (
    #         '1',
    #         '2 > 21',
    #         '2 > 22',
    #         '2 > 23 > 231',
    #         '2 > 24',
    #         '3',
    #         '4 > 41',
    #     )
    #     for breadcrumbs in categories:
    #         create_from_breadcrumbs(breadcrumbs)
    #
    # def test_new_product(self):
    #     """
    #     test latest Products
    #     Returns:
    #         None
    #     """
    #     test_catalogue.create_product_bulk()
    #     with self.assertNumQueries(5):
    #         response = self.client.post(reverse('promotions:new'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(200, response.status_code)
    #     products = Product.objects.prefetch_related(
    #         Prefetch('images'),
    #         Prefetch('categories')
    #     ).order_by('-date_created')[:MAX_COUNT_PRODUCT]
    #     products = [product.get_values() for product in products]
    #     self.assertJSONEqual(json.dumps(products), response.content)
    #
    # def test_recommend_product(self):
    #     """
    #     test list recommend product from model ProductRecommendation
    #     Returns:
    #         None
    #     """
    #     test_catalogue.create_product_bulk_recommend()
    #     with self.assertNumQueries(5):
    #         response = self.client.post(reverse('promotions:recommend'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(200, response.status_code)
    #     object_list = ProductRecommendation.objects.select_related('recommendation').prefetch_related(
    #         Prefetch('recommendation__images'),
    #         Prefetch('recommendation__categories')
    #     ).order_by('-recommendation__date_created')[:MAX_COUNT_PRODUCT]
    #     products = [recommend.recommendation.get_values() for recommend in object_list]
    #     self.assertJSONEqual(json.dumps(products), response.content)
