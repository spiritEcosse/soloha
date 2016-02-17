# --coding: utf-8--

from django.test import TestCase
from django.test import Client
from oscar.core.loading import get_class, get_model
from oscar.test.factories import create_product
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import IMAGE_NOT_FOUND
from apps.catalogue.models import ProductImage
from oscar.apps.partner.strategy import Selector
from oscar.test import factories
from django.utils.html import strip_entities
from apps.catalogue.models import ProductAttribute, AttributeOptionGroup, AttributeOption, ProductAttributeValue


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
        image = product.primary_image()

        if isinstance(image, ProductImage):
            image = image.original
        else:
            image = IMAGE_NOT_FOUND

        values['image'] = get_thumbnailer(image).get_thumbnail(options).url
        self.assertDictEqual(values, product.get_values())

    def _create_product_attribute(self):
        option_group = AttributeOptionGroup.objects.create(name='Size')
        product_attribute = ProductAttribute.objects.create(name='Size', code='size', type='option', option_group=option_group)
        product = factories.create_product()
        product_attr_value = []

        attribute_values = (
            {'option': 'extra small', 'pos': False},
            {'option': 'small', 'pos': True},
            {'option': 'medium', 'pos': False},
            {'option': 'extra large', 'pos': True},
            {'option': 'large', 'pos': True}
        )

        for value in attribute_values:
            kwargs_product_attr_value = {
                'attribute': product_attribute,
                'product': product,
                'value_option': AttributeOption.objects.create(option=value['option'], group=option_group),
                self.pos: value['pos'],
            }

            if value['pos'] is self.needle:
                product_attr_value.append(ProductAttributeValue.objects.create(**kwargs_product_attr_value))

        return product, product_attr_value

    def test_product_attributes(self):
        """
        get attributes from product where pos_... = True or False
        Returns:
        None
        """
        self.needle = True
        self.pos = 'pos_option'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_option=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = False
        self.pos = 'pos_option'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_option=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = True
        self.pos = 'pos_attribute'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_attribute=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = False
        self.pos = 'pos_attribute'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_attribute=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = True
        self.pos = 'pos_filter'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_filter=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = False
        self.pos = 'pos_filter'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_filter=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = True
        self.pos = 'pos_characteristic'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_characteristic=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))

        self.needle = False
        self.pos = 'pos_characteristic'
        product, expected_product_attr_value = self._create_product_attribute()
        received_product_attr_value = ProductAttributeValue.objects.filter(product=product, pos_characteristic=self.needle)
        self.assertListEqual(expected_product_attr_value, list(received_product_attr_value))
