# --coding: utf-8--

from django.test import TestCase
from django.test import Client
from oscar.core.loading import get_class, get_model
from oscar.test.factories import create_product
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import IMAGE_NOT_FOUND
from oscar.apps.partner.strategy import Selector
from oscar.test import factories
from django.utils.html import strip_entities
from django.core.urlresolvers import reverse
import json
from django.db.models.query import Prefetch


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

    def test_url_product(self):
        product = create_product()
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        self.create_category()
        category = Category.objects.get(name='21')
        product_category = ProductCategory(product=product, category=category)
        product_category.save()
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

    def test_url_category(self):
        self.create_category()
        category = Category.objects.get(name='231')
        response = self.client.get(category.get_absolute_url())
        self.assertEqual(response.request['PATH_INFO'], category.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)

    def test_url_catalogue(self):
        catalogue = '/catalogue/'
        response = self.client.get(catalogue)
        self.assertEqual(response.request['PATH_INFO'], catalogue)
        self.assertEqual(response.status_code, STATUS_CODE_200)

    def test_product_values(self):
        product = factories.create_product()
        factories.create_product_image(product, original=IMAGE_NOT_FOUND)

        values = dict()
        values['title'] = strip_entities(product.title)
        values['absolute_url'] = product.get_absolute_url()
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(product)
        values['price'] = str(info.price.incl_tax)
        options = {'size': (220, 165), 'crop': True}
        values['image'] = get_thumbnailer(getattr(product.primary_image(), 'original', IMAGE_NOT_FOUND)).get_thumbnail(options).url
        self.assertDictEqual(values, product.get_values())

        # def _create_product_attribute(self):
        #     option_group = AttributeOptionGroup.objects.create(name='Size')
        #     product_attribute = ProductAttribute.objects.create(name='Size', code='size', type='option', option_group=option_group)
        #     product = factories.create_product()
        #     product_attr_value = []
        #
        #     attribute_values = (
        #         {'option': 'extra small', 'pos': False},
        #         {'option': 'small', 'pos': True},
        #         {'option': 'medium', 'pos': False},
        #         {'option': 'extra large', 'pos': True},
        #         {'option': 'large', 'pos': True}
        #     )
        #
        #     for value in attribute_values:
        #         kwargs_product_attr_value = {
        #             'attribute': product_attribute,
        #             'product': product,
        #             'value_option': AttributeOption.objects.create(option=value['option'], group=option_group),
        #             self.pos: value['pos'],
        #         }
        #
        #         if value['pos'] is self.needle:
        #             product_attr_value.append(ProductAttributeValue.objects.create(**kwargs_product_attr_value))
        #
        #     return product, product_attr_value

        # def test_product_attributes(self):
        #     """
        #     get attributes from product where pos_... = True or False
        #     Returns:
        #     None
        #     """
        #     self.needle = True
        #     self.pos = 'pos_option'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_option=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = False
        #     self.pos = 'pos_option'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_option=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = True
        #     self.pos = 'pos_attribute'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_attribute=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = False
        #     self.pos = 'pos_attribute'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_attribute=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = True
        #     self.pos = 'pos_filter'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_filter=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = False
        #     self.pos = 'pos_filter'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_filter=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = True
        #     self.pos = 'pos_characteristic'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_characteristic=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
        #
        #     self.needle = False
        #     self.pos = 'pos_characteristic'
        #     product, expected_product_attr_value = self._create_product_attribute()
        #     received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_characteristic=self.needle)
        #     self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

    def test_category_get_values(self):
        """

        Returns:

        """
        self.create_category()
        category = Category.objects.get(name='1')
        must = {
            'name': category.name,
            'icon': category.get_icon(),
            'absolute_url': category.get_absolute_url(),
            'slug': category.slug,
            'image_banner': category.get_image_banner(),
            'link_banner': category.link_banner,
        }
        really = category.get_values()
        self.assertDictEqual(must, really)

    def get_load_data(self):
        """
        get data for model category
        Returns:
        Examples
        in key data store fields model category
        in key children store list children model category
        [
            {'data': {'name': '1', 'sort': 1}},
            {'data': {'name': '2', 'sort': 2}, 'children': [
                {'data': {'name': '21', 'sort': 1}},
                {'data': {'name': '22', 'sort': 2}},
                {'data': {'name': '23', 'sort': 3}, 'children': [
                    {'data': {'name': '231', 'sort': 1}},
                ]},
                {'data': {'name': '24', 'sort': 3}},
            ]},
            {'data': {'name': '3', 'sort': 4}},
            {'data': {'name': '4', 'sort': 5}, 'children': [
                {'data': {'name': '41', 'sort': 1}},
            ]},
        ]
        """
        return [
            {'data': {'name': '1', 'sort': 1}},
            {'data': {'name': '2', 'sort': 0}, 'children': [
                {'data': {'name': '24', 'sort': 0}},
                {'data': {'name': '21', 'sort': 1}},
                {'data': {'name': '22', 'sort': 2}},
                {'data': {'name': '23', 'sort': 3}, 'children': [
                    {'data': {'name': '231', 'sort': 1}},
                ]},
            ]},
            {'data': {'name': '3', 'sort': 2}},
            {'data': {'name': '4', 'sort': -5}, 'children': [
                {'data': {'name': '41', 'sort': 1}},
            ]},
        ]

    def test_dump_bulk_depth(self):
        Category.load_bulk(self.get_load_data())
        load_data = list()
        load_data.append({'data': Category.objects.get(name='4').get_values()})
        load_data.append({'data': Category.objects.get(name='2').get_values()})
        load_data.append({'data': Category.objects.get(name='1').get_values()})
        load_data.append({'data': Category.objects.get(name='3').get_values()})
        dump_bulk_depth_data = Category.dump_bulk_depth(max_depth=1, keep_ids=False)
        self.assertListEqual(load_data, dump_bulk_depth_data)

        load_data = list()
        load_data.append({
            'data': Category.objects.get(name='4').get_values(),
            'children': [{'data': Category.objects.get(name='41').get_values()}]
        })
        load_data.append({
            'data': Category.objects.get(name='2').get_values(),
            'children': [
                {'data': Category.objects.get(name='24').get_values()},
                {'data': Category.objects.get(name='21').get_values()},
                {'data': Category.objects.get(name='22').get_values()},
                {'data': Category.objects.get(name='23').get_values()},
            ]
        })
        load_data.append({'data': Category.objects.get(name='1').get_values()})
        load_data.append({'data': Category.objects.get(name='3').get_values()})
        dump_bulk_depth_data = Category.dump_bulk_depth(max_depth=2, keep_ids=False)
        self.assertListEqual(load_data, dump_bulk_depth_data)

        load_data = list()
        load_data.append({
            'data': Category.objects.get(name='4').get_values(),
            'children': [{'data': Category.objects.get(name='41').get_values()}]
        })
        load_data.append({
            'data': Category.objects.get(name='2').get_values(),
            'children': [
                {'data': Category.objects.get(name='24').get_values()},
                {'data': Category.objects.get(name='21').get_values()},
                {'data': Category.objects.get(name='22').get_values()},
                {
                    'data': Category.objects.get(name='23').get_values(),
                    'children': [{'data': Category.objects.get(name='231').get_values()}]
                },
            ]
        })
        load_data.append({'data': Category.objects.get(name='1').get_values()})
        load_data.append({'data': Category.objects.get(name='3').get_values()})
        dump_bulk_depth_data = Category.dump_bulk_depth(max_depth=3, keep_ids=False)
        self.assertListEqual(load_data, dump_bulk_depth_data)

        load_data = list()
        load_data.append({
            'data': Category.objects.get(name='4').get_values(),
            'children': [{'data': Category.objects.get(name='41').get_values()}]
        })
        load_data.append({
            'data': Category.objects.get(name='2').get_values(),
            'children': [
                {'data': Category.objects.get(name='24').get_values()},
                {'data': Category.objects.get(name='21').get_values()},
                {'data': Category.objects.get(name='22').get_values()},
                {
                    'data': Category.objects.get(name='23').get_values(),
                    'children': [{'data': Category.objects.get(name='231').get_values()}]
                },
            ]
        })
        load_data.append({'data': Category.objects.get(name='1').get_values()})
        load_data.append({'data': Category.objects.get(name='3').get_values()})
        dump_bulk_depth_data = Category.dump_bulk_depth(max_depth=0, keep_ids=False)
        self.assertListEqual(load_data, dump_bulk_depth_data)

    def test_get_list_product(self):
        """
        get list product by current category
        Returns:
        None
        """
        self.create_category()
        category = Category.objects.get(name='231')
        product = create_product()
        product_category = ProductCategory(product=product, category=category)
        product_category.save()
        response = self.client.post(reverse('catalogue:products'), {'category_pk': category.pk}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        products_queryset = Product.objects.filter(categories=category.pk).prefetch_related(
            Prefetch('images'),
            Prefetch('categories'),
        ).order_by('-date_created')
        products = [product.get_values() for product in products_queryset]
        self.assertJSONEqual(response.content, json.dumps(products))
