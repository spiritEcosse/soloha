from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from oscar.test import factories
from oscar.apps.order.models import Line
from apps.catalogue.models import Product
from soloha.settings import MAX_COUNT_PRODUCT
from apps.catalogue.models import ProductRecommendation
import json
from django.db.models.query import Prefetch
from oscar.core.loading import get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from django import db
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'productcategory')


class TestHomePage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hits_product(self):
        factories.create_order()
        response = self.client.post(reverse('promotions:hits'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        products = [line.product.get_values() for line in Line.objects.order_by('-product__date_created')[:MAX_COUNT_PRODUCT]]
        self.assertJSONEqual(response.content, json.dumps(products))

    def create_category(self):
        categories = (
            '1',
            '2 > 21',
            '2 > 22',
            '2 > 23 > 231',
            '2 > 24',
            '3',
            '4 > 41',
        )
        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)

    def create_product_bulk(self):
        self.create_category()

        for num in xrange(1, 100):
            product = factories.create_product(title='Product {}'.format(num))
            factories.create_product_image(product=product)
            category = Category.objects.get(name='231')
            product_category = ProductCategory(product=product, category=category)
            product_category.save()

    def test_new_product(self):
        self.create_product_bulk()
        with self.assertNumQueries(5):
            response = self.client.post(reverse('promotions:new'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        products = Product.objects.prefetch_related(
            Prefetch('images'),
            Prefetch('categories')
        ).order_by('-date_created')[:MAX_COUNT_PRODUCT]
        products = [product.get_values() for product in products]
        self.assertJSONEqual(response.content, json.dumps(products))

    # def test_special_product(self):
    #     factories.create_product()
    #     response = self.client.post(reverse('promotions:special'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(200, response.status_code)
    #     # products = Product.objects.all()[:10]
    #     # products = serializers.serialize("json", products)
    #     # self.assertJSONEqual(response.content, products)

    def create_product_bulk_recommend(self):
        self.create_product_bulk()
        product_desc = Product.objects.all().order_by('-date_created')
        product_asc = Product.objects.all().order_by('date_created')

        for num in xrange(0, len(product_desc)):
            ProductRecommendation.objects.create(primary=product_desc[num], recommendation=product_asc[num])

    def test_recommend_product(self):
        self.create_product_bulk_recommend()
        with self.assertNumQueries(5):
            response = self.client.post(reverse('promotions:recommend'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        object_list = ProductRecommendation.objects.select_related('recommendation').prefetch_related(
            Prefetch('recommendation__images'),
            Prefetch('recommendation__categories')
        ).order_by('-recommendation__date_created')[:MAX_COUNT_PRODUCT]
        products = [recommend.recommendation.get_values() for recommend in object_list]
        self.assertJSONEqual(response.content, json.dumps(products))

    def get_categories(self):
        categories = (
            'Food > Cheese',
            'Food > Meat',
            'Clothes > Man > Jackets',
            'Clothes > Woman > Skirts',
        )
        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)

        response = self.client.post(reverse('promotions:categories'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # categories = Category.get_root_nodes().filter(enable=True).order_by('name').only('name')
        categories = Category.get_annotated_list()
        self.assertJSONEqual(response.content, json.dumps(categories))
