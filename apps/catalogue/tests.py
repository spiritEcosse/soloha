# --coding: utf-8--

from django.test import TestCase
from django.test import Client
# from slugify import UniqueSlugify
from oscar.core.loading import get_class, get_model
from oscar.test.factories import create_product
from oscar.apps.catalogue.categories import create_from_breadcrumbs

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'ProductCategory')

STATUS_CODE_200 = 200


class TestCatalog(TestCase):
    def setUp(self):
        self.client = Client()

    def create_category(self):
        categories = (
            'Clothes > Woman > Skirts',
        )
        for breadcrumbs in categories:
            create_from_breadcrumbs(breadcrumbs)

    def test_url_product(self):
        product = create_product()
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        self.create_category()
        category = Category.objects.get(name='Skirts')
        product_category = ProductCategory(product=product, category=category)
        product_category.save()
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

    def test_url_category(self):
        self.create_category()
        category = Category.objects.get(name='Skirts')
        response = self.client.get(category.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], category.get_absolute_url())

    def test_url_catalogue(self):
        catalogue = '/catalogue/'
        response = self.client.get(catalogue)
        self.assertEqual(response.request['PATH_INFO'], catalogue)
