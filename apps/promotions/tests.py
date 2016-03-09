from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from oscar.test import factories
from oscar.apps.order.models import Line
from apps.catalogue.models import Product
from soloha.settings import MAX_COUNT_PRODUCT
from apps.catalogue.models import ProductRecommendation
from apps.promotions.views import RecommendView
import json
from django.db.models.query import Prefetch
from oscar.core.loading import get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from apps.catalogue.tests import get_annotated_list
Category = get_model('catalogue', 'category')


class TestHomePage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_hits_product(self):
        factories.create_order()
        response = self.client.post(reverse('promotions:hits'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        products = [line.product.get_values() for line in Line.objects.order_by('-product__date_created')[:MAX_COUNT_PRODUCT]]
        self.assertJSONEqual(response.content, json.dumps(products))

    def test_new_product(self):
        factories.create_product(title='Product 1')
        factories.create_product(title='Product 2')
        response = self.client.post(reverse('promotions:new'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        products = Product.objects.order_by('-date_created')[:MAX_COUNT_PRODUCT]
        products = [product.get_values() for product in products]
        self.assertJSONEqual(response.content, json.dumps(products))

    # def test_special_product(self):
    #     factories.create_product()
    #     response = self.client.post(reverse('promotions:special'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    #     self.assertEqual(200, response.status_code)
    #     # products = Product.objects.all()[:10]
    #     # products = serializers.serialize("json", products)
    #     # self.assertJSONEqual(response.content, products)

    def test_recommend_product(self):
        product_1 = factories.create_product(title='Product 1')
        product_2 = factories.create_product(title='Product 2')
        product_3 = factories.create_product(title='Product 3')
        product_4 = factories.create_product(title='Product 4')
        product_5 = factories.create_product(title='Product 5')

        ProductRecommendation.objects.create(primary=product_1, recommendation=product_2)
        ProductRecommendation.objects.create(primary=product_1, recommendation=product_3)
        ProductRecommendation.objects.create(primary=product_2, recommendation=product_3)
        ProductRecommendation.objects.create(primary=product_2, recommendation=product_4)
        ProductRecommendation.objects.create(primary=product_3, recommendation=product_5)

        queryset_product = Product.objects.only('title')

        # with self.assertNumQueries(6):
        response = self.client.post(reverse('promotions:recommend'), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        object_list = ProductRecommendation.objects.prefetch_related(
            Prefetch('recommendation', queryset=queryset_product),
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
        categories = get_annotated_list()
        self.assertJSONEqual(response.content, json.dumps(categories))
