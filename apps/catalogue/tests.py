# --coding: utf-8--

import json
import random
from decimal import Decimal as D

from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count
from django.db.models import Min
from django.db.models import Q
from django.db.models.query import Prefetch
from django.test import Client
from django.test import LiveServerTestCase
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from oscar.apps.partner.strategy import Selector
from oscar.core.loading import get_model
from oscar.test import factories
from selenium import webdriver
from selenium.webdriver.support.select import Select

from apps.catalogue.views import ProductCategoryView, ProductDetailView
from python_test.factories import catalogue
from soloha import settings
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from templatetags.filters_concatenation import concatenate
import time

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductOptions = get_model('catalogue', 'ProductOptions')
VersionAttribute = get_model('catalogue', 'VersionAttribute')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductVersion = get_model('catalogue', 'ProductVersion')
Feature = get_model('catalogue', 'Feature')
test_catalogue = catalogue.Test()

STATUS_CODE_200 = 200


class TestCatalog(LiveServerTestCase):
    css_selector_product_price = 'div#section3 .price .wrapper-number .number'
    css_selector_attribute = '.options .panel-default:nth-child({})'

    def setUp(self):
        self.client = Client()
        self.firefox = webdriver.Firefox()
        self.firefox.maximize_window()
        super(TestCatalog, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        time.sleep(2)
        self.firefox.quit()
        time.sleep(2)
        super(TestCatalog, self).tearDown()

    def test_page_product(self):
        """
        accessibility page product
        Returns:
            None
        """
        test_catalogue.create_product_bulk()
        product = Product.objects.get(title='Product 1')
        response = self.client.get(product.get_absolute_url())
        self.equal = self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        product = Product.objects.get(title='Product 20')
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        product = Product.objects.get(title='Product 39')
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        test_catalogue.test_menu_categories(obj=self, response=response)

    def get_product_version(self, product):
        # ToDo igor: add to order_by - 'parent__product_features__sort'
        return ProductVersion.objects.filter(product=product).prefetch_related('attributes').order_by('price_retail')

    def get_product_price(self, product):
        """
        get main price for product
        :param product: obj product
        :return:
            context
        """
        context = {}
        first_prod_version = self.get_product_version(product=product).first()

        # ToDo make it possible to check whether the product is available for sale
        if not first_prod_version:
            selector = Selector()
            strategy = selector.strategy()
            info = strategy.fetch_for_product(product)

            if info.availability.is_available_to_buy:
                context['price'] = info.price.incl_tax
                context['currency'] = info.price.currency
            else:
                context['price'] = str(_('Product is not available.'))
        else:
            price = first_prod_version.price_retail
            for attribute in first_prod_version.version_attributes.all():
                if attribute.plus:
                    price += attribute.price_retail
            context['price'] = price
            context['currency'] = settings.OSCAR_DEFAULT_CURRENCY
        return context

    def get_dict_product_version_price(self, product):
        dict_product_version_price = dict()

        for product_version in self.get_product_version(product=product):
            attribute_values = []
            price = product_version.price_retail
            version_attributes = product_version.version_attributes.filter(
                attribute__parent__children__product_versions__product=product, attribute__level=1,
                attribute__parent__level=0
            ).annotate(
                price=Min('version__price_retail'),
                count_child=Count('attribute__parent__children', distinct=True)
            ).order_by('attribute__parent__product_features__sort', 'price', '-count_child', 'attribute__parent__title', 'attribute__parent__pk')
            for version_attribute in version_attributes:
                attribute_values.append(str(version_attribute.attribute.pk))
                if version_attribute.plus:
                    price += version_attribute.price_retail
            dict_product_version_price[','.join(attribute_values)] = str(price)

        return dict_product_version_price

    def test_product_post(self):
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        product_2 = Product.objects.get(slug='product-2')
        test_catalogue.create_options(product, product_2)

        response = self.client.post(product.get_absolute_url(), content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = json.loads(response.content)

        expected_context = dict()
        expected_context['product_versions'] = self.get_dict_product_version_price(product=product)
        expected_context['attributes'] = []
        for attr in self.get_product_attributes(product=product):
            values = [{'id': value.pk, 'title': value.title} for value in attr.values]
            expected_context['attributes'].append({'pk': attr.pk, 'title': attr.title, 'values': values})

        self.assertDictEqual(context['product_versions'], expected_context['product_versions'])
        self.assertListEqual(context['attributes'], expected_context['attributes'])

    def get_product_attributes(self, product):
        only = ['title', 'pk']
        return Feature.objects.only(*only).filter(
            children__product_versions__product=product, level=0
        ).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*only).filter(
                level=1, product_versions__product=product
            ).annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values')
        ).annotate(price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)).\
            order_by('product_features__sort', 'price', '-count_child', 'title', 'pk')

    def test_get_price_product_selenium(self):
        """
        test price for product with state track_stock
        :return:
        """
        test_catalogue.create_categories()
        product_class_with_track_stock = ProductClass.objects.create(name='Product class where track_stock is True')
        num = 1
        product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=D('12.12'),
                                           product_class=product_class_with_track_stock)

        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(price, str(context['price']))
        self.assertEqual(price, str(_('Product is not available.')))

        product_class_without_track_stock, created = ProductClass.objects.get_or_create(name='Product class where track_stock is False', track_stock=False)
        num = 2
        product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=D('15.13'),
                                           product_class=product_class_without_track_stock)
        test_catalogue.create_attributes(product)
        test_catalogue.create_options(product, product)

        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))
        time.sleep(1)
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(price, str(context['price']))
        self.assertEqual(price, str(D('1.10')))

        product_class_without_track_stock, created = ProductClass.objects.get_or_create(name='Product class where track_stock is False', track_stock=False)
        num = 3
        product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=D('15.13'),
                                           product_class=product_class_without_track_stock)
        test_catalogue.create_attribute_option(product=product)
        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))
        time.sleep(1)
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(price, str(context['price']))
        self.assertEqual(price, str(D('112.20')))

    def test_page_product_attribute_dynamic_attributes(self):
        """
        test page product with attributes by selenium
        :return:
        """
        test_catalogue.create_product_bulk()
        product = factories.create_product(slug='product-attributes', title='Product attributes', price=D(random.randint(1, 10000)))
        test_catalogue.create_dynamic_attributes(product)
        attributes = list(self.get_product_attributes(product=product))
        product_versions = self.get_dict_product_version_price(product=product)
        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))

        start_price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(start_price, str(context['price']))

        feature_11 = Feature.objects.get(title='Feature 11')
        feature_21 = Feature.objects.get(title='Feature 21')
        feature_22 = Feature.objects.get(title='Feature 22')
        feature_31 = Feature.objects.get(title='Feature 31')
        feature_32 = Feature.objects.get(title='Feature 32')
        feature_33 = Feature.objects.get(title='Feature 33')

        selectable_attributes = [feature_11, feature_21, feature_31]
        price_11_21_31 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2100.00')), price_11_21_31)

        selectable_attributes = [feature_11, feature_21, feature_32]
        price_11_21_32 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2200.00')), price_11_21_32)

        selectable_attributes = [feature_11, feature_21, feature_33]
        price_11_21_33 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2300.00')), price_11_21_33)

        selectable_attributes = [feature_11, feature_22, feature_31]
        price_11_22_31 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2400.00')), price_11_22_31)

        selectable_attributes = [feature_11, feature_22, feature_32]
        price_11_22_32 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2500.00')), price_11_22_32)

        selectable_attributes = [feature_11, feature_22, feature_33]
        price_11_22_33 = self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions)
        self.assertEqual(str(D('2700.00')), price_11_22_33)

        selectable_attributes = [feature_11, feature_21, feature_31]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_21_31)
        self.assertEqual(str(D('2100.00')), price_11_21_31)

        selectable_attributes = [feature_11, feature_21, feature_32]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_21_32)
        self.assertEqual(str(D('2200.00')), price_11_21_32)

        selectable_attributes = [feature_11, feature_21, feature_33]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_21_33)
        self.assertEqual(str(D('2300.00')), price_11_21_33)

        selectable_attributes = [feature_11, feature_22, feature_31]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_22_31)
        self.assertEqual(str(D('2400.00')), price_11_22_31)

        selectable_attributes = [feature_11, feature_22, feature_32]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_22_32)
        self.assertEqual(str(D('2500.00')), price_11_22_32)

        selectable_attributes = [feature_11, feature_22, feature_33]
        self.select_attribute(selectable_attributes=selectable_attributes, attributes=attributes, product_versions=product_versions, earlier_price=price_11_22_33)
        self.assertEqual(str(D('2700.00')), price_11_22_33)

    def select_attribute(self, selectable_attributes, attributes, product_versions, earlier_price=None):
        last_attribute = selectable_attributes.pop()

        for attribute in selectable_attributes:
            self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes, product_versions=product_versions)

        return self.checkout_price_by_selected_attribute(attribute=last_attribute, attributes=attributes, product_versions=product_versions, earlier_price=earlier_price)

    def test_page_product_attributes_selenium(self):
        """
        test page product with ordered attributes by selenium
        :return:
        """
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        attributes = self.get_product_attributes(product=product)

        product_versions = self.get_dict_product_version_price(product=product)
        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))

        start_price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(start_price, str(context['price']))

        attributes_real = []
        for position in xrange(1, len(attributes) + 1):
            attribute = self.firefox.find_element_by_css_selector(self.css_selector_attribute.format(position))
            attributes_real.append(attribute.find_element_by_css_selector('.name').text)

        self.assertListEqual(attributes_real, [attribute.title for attribute in attributes])

        list_price = product_versions.values()
        self.assertEqual(start_price in list_price, True)

        attributes = list(attributes)
        attribute_33 = Feature.objects.get(title='Feature 33')
        attribute_32 = Feature.objects.get(title='Feature 32')
        attribute_31 = Feature.objects.get(title='Feature 31')
        self.checkout_price_by_selected_attribute(attribute=attribute_33, attributes=attributes, product_versions=product_versions, earlier_price=start_price)
        price_32 = self.checkout_price_by_selected_attribute(attribute=attribute_32, attributes=attributes, product_versions=product_versions)
        price_31 = self.checkout_price_by_selected_attribute(attribute=attribute_31, attributes=attributes, product_versions=product_versions)
        price_33 = self.checkout_price_by_selected_attribute(attribute=attribute_33, attributes=attributes, product_versions=product_versions)
        self.checkout_price_by_selected_attribute(attribute=attribute_31, attributes=attributes, product_versions=product_versions, earlier_price=price_31)
        self.checkout_price_by_selected_attribute(attribute=attribute_32, attributes=attributes, product_versions=product_versions, earlier_price=price_32)
        self.checkout_price_by_selected_attribute(attribute=attribute_33, attributes=attributes, product_versions=product_versions, earlier_price=start_price)

        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))
        self.checkout_price_by_selected_attribute(attribute=attribute_32, attributes=attributes, product_versions=product_versions, earlier_price=price_32)
        self.checkout_price_by_selected_attribute(attribute=attribute_31, attributes=attributes, product_versions=product_versions, earlier_price=price_31)
        self.checkout_price_by_selected_attribute(attribute=attribute_33, attributes=attributes, product_versions=product_versions, earlier_price=price_33)

    def checkout_price_by_selected_attribute(self, attribute, attributes, product_versions, earlier_price=None):
        index_attr = attributes.index(attribute.parent)
        expect_attribute = attributes[index_attr]
        attribute_1 = self.firefox.find_element_by_css_selector(self.css_selector_attribute.format(index_attr + 1))
        self.assertEqual(attribute_1.find_element_by_css_selector('.name').text, expect_attribute.title)

        attribute_1_values = attribute_1.find_element_by_css_selector('select')
        self.assertListEqual(attribute_1_values.text.split('\n'), [value.title for value in expect_attribute.values])

        index_attr_val = expect_attribute.values.index(attribute)
        attr_val = expect_attribute.values[index_attr_val]
        Select(attribute_1_values).select_by_visible_text(attr_val.title)

        selected_values = []
        for num in xrange(1, len(attributes) + 1):
            selector = Select(self.firefox.find_element_by_css_selector('%s select' % self.css_selector_attribute.format(num)))
            selected_values.append(int(selector.first_selected_option.get_attribute('value')))

        expected_price = product_versions.get(','.join(map(str, selected_values)))
        time.sleep(1)
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        time.sleep(1)
        self.assertEqual(price, str(expected_price))

        if earlier_price is not None:
            self.assertEqual(price, earlier_price)

        return price

    def test_get_product_attributes(self):
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        response = self.client.get(product.get_absolute_url())

        attributes = self.get_product_attributes(product=product)
        self.assertEqual(str(attributes.query), str(response.context['attributes'].query))
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.resolver_match.func.__name__, ProductDetailView.as_view().__name__)
        self.assertTemplateUsed(response, 'catalogue/detail.html')
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())
        self.assertEqual(product, response.context['product'])
        self.assertEqual(len(attributes), len(response.context['attributes']))
        attributes_expected = [(attr, attr.values) for attr in attributes]
        attributes_real = [(attr, attr.values) for attr in response.context['attributes']]
        self.assertListEqual(attributes_expected, attributes_real)
        test_catalogue.test_menu_categories(obj=self, response=response)

    def test_url_catalogue(self):
        """
        accessibility page catalogue
        Returns:
            None
        """
        catalogue = '/catalogue/'
        response = self.client.get(catalogue)
        self.assertEqual(response.request['PATH_INFO'], catalogue)
        self.assertEqual(response.status_code, STATUS_CODE_200)
        test_catalogue.test_menu_categories(obj=self, response=response)

    def test_get_full_slug(self):
        """
        check the correctness of full slug
        :return:
        """
        test_catalogue.create_categories()
        category_1 = Category.objects.get(name='Category-1')
        self.assertEqual(category_1.slug, category_1.full_slug)
        category_12 = Category.objects.get(name='Category-12')
        slugs = [category_12.parent.slug, category_12.slug]
        self.assertEqual(category_12._slug_separator.join(map(str, slugs)), category_12.full_slug)
        category_1234 = Category.objects.get(name='Category-1234')
        slugs = [category_1234.parent.parent.parent.slug, category_1234.parent.parent.slug, category_1234.parent.slug, category_1234.slug]
        self.assertEqual(Category._slug_separator.join(map(str, slugs)), category_1234.full_slug)

    def create_duplicate_version_attribute(self):
        product, created = Product.objects.get_or_create(slug='test')
        feature_11, created = Feature.objects.get_or_create(title='Feature 11')

        message = "UNIQUE constraint failed: catalogue_versionattribute.version_id, catalogue_versionattribute.attribute_id"

        with self.assertRaisesMessage(expected_exception=IntegrityError, expected_message=message):
            price_retail = D(random.randint(1, 10000))
            product_version_1, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

            VersionAttribute.objects.create(version=product_version_1, attribute=feature_11)
            VersionAttribute.objects.create(version=product_version_1, attribute=feature_11)

    def create_duplicate_product_version_attribute(self):
        product, created = Product.objects.get_or_create(slug='test')
        feature_11, created = Feature.objects.get_or_create(title='Feature 11')
        feature_21, created = Feature.objects.get_or_create(title='Feature 21')
        feature_31, created = Feature.objects.get_or_create(title='Feature 31')

        message = 'UNIQUE constraint failed: catalogue_productversion.version_id, catalogue_productversion.attribute_id'

        with self.assertRaisesMessage(expected_exception=IntegrityError, expected_message=message):
            price_retail = D(random.randint(1, 10000))
            product_version_1, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

            VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_11)
            VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_21)
            VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_31)

            price_retail = D(random.randint(1, 10000))
            product_version_2, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

            VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_11)
            VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_21)
            VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_31)

    def test_create_product(self):
        message = 'UNIQUE constraint failed: catalogue_product.slug'

        with self.assertRaisesMessage(expected_exception=IntegrityError, expected_message=message):
            Product.objects.create(title='Product-1')
            Product.objects.create(title='Product-1')

    def test_create_feature(self):
        message = 'UNIQUE constraint failed: catalogue_feature.slug'

        with self.assertRaisesMessage(expected_exception=IntegrityError, expected_message=message):
            Feature.objects.create(title='Feature-1')
            Feature.objects.create(title='Feature-1')

    def test_page_category(self):
        """
        Check the availability of a specific category page template, type the name of the class, true to the object
        of a category, a fixed amount of goods in the different versions of the tree search.
        Returns:
            None
        """
        test_catalogue.create_product_bulk()
        # without products in this category has no descendants in the categories at the same time this very category and its children is not goods
        dict_values = {'num_queries': 10}
        category = Category.objects.get(name='Category-2')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this child category are not the descendants of the categories at the same time, this category has itself in goods
        # Todo: why 24 queries ?
        dict_values = {'num_queries': 24}
        category = Category.objects.get(name='Category-321')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this category has category of descendants with itself, this category is not in goods, but its descendants have in the goods
        dict_values = {'num_queries': 20}
        category = Category.objects.get(name='Category-1')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products with this main category has no descendants of categories at the same time, this category has itself in goods
        dict_values = {'num_queries': 18}
        category = Category.objects.get(name='Category-4')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this category is that the main categories of the children with this very category and its descendants have in the goods
        dict_values = {'num_queries': 18}
        category = Category.objects.get(name='Category-3')
        self.assertions_category(category=category, dict_values=dict_values)

    def test_page_category_paginator(self):
        test_catalogue.create_product_bulk()

        dict_values = {'num_queries': 20}
        category = Category.objects.get(name='Category-12')
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 1, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

    def test_page_category_sorting_with_filters(self):
        test_catalogue.create_product_bulk()

        category = Category.objects.get(name='Category-12')
        category_1 = Category.objects.get(name='Category-1')
        category_2 = Category.objects.get(name='Category-2')
        category_321 = Category.objects.get(name='Category-321')

        dict_values = {'page': 1, 'sorting_type': 'price_ascending', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        self.assertions_category(category=category_321, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'popularity', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20, 'filters': ''}
        self.assertions_category(category=category, dict_values=dict_values)
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        self.assertions_category(category=category_321, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1100/shirina_1200/dlina_1000/dlina_1100'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'popularity', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'popularity', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        # self.assertions_category(category=category_321, dict_values=dict_values)

    def test_page_category_sort(self):
        test_catalogue.create_product_bulk()

        category = Category.objects.get(name='Category-12')

        # Sorted by price ascending
        dict_values = {'page': 1, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        # TODO use price_retail

        # sorting by price descending
        dict_values = {'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'price_descending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'price_descending', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

        # sorting by rating
        dict_values = {'page': 1, 'sorting_type': 'popularity', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'popularity', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'popularity', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

    def assertions_category(self, category, dict_values={}):
        paginate_by = OSCAR_PRODUCTS_PER_PAGE
        only = ['title', 'slug', 'structure', 'product_class', 'enable', 'categories', 'filters']
        dict_filter = {'enable': True, 'categories__in': category.get_descendants(include_self=True)}

        if dict_values.get('filter_slug'):
            dict_filter['filters__slug__in'] = dict_values.get('filter_slug').split('/')

        response = self.client.get(category.get_absolute_url(), dict_values)

        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                'price_descending': '-stockrecords__price_excl_tax'}
        dict_values['sorting_type'] = dict_new_sorting_types.get(dict_values.get('sorting_type'), '-views_count')

        products = Product.objects.filter(**dict_filter).only(*only).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(dict_values['sorting_type'])

        products_without_filters = Product.objects.only('id').filter(**dict_filter).distinct().order_by(dict_values['sorting_type'])

        queryset_filters = Feature.objects.filter(filter_products__in=products_without_filters).distinct().prefetch_related('filter_products')
        filters = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters, to_attr='children_in_products'),
        ).distinct()

        p = Paginator(products, paginate_by)

        # with self.assertNumQueries(dict_values['num_queries']):
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.resolver_match.func.__name__, ProductCategoryView.as_view().__name__)
        self.assertTemplateUsed(response, 'catalogue/category.html')
        self.assertEqual(response.request['PATH_INFO'], category.get_absolute_url())
        self.assertEqual(category, response.context['category'])
        self.assertEqual(len(p.page(dict_values.get('page', 1)).object_list), len(response.context['page_obj']))
        self.assertListEqual(list(p.page(dict_values.get('page', 1)).object_list), list(response.context['page_obj']))
        self.assertEqual(p.count, response.context['paginator'].count)
        self.assertEqual(p.num_pages, response.context['paginator'].num_pages)
        self.assertEqual(p.page_range, response.context['paginator'].page_range)
        self.assertEqual(list(filters), list(response.context['filters']))

        test_catalogue.test_menu_categories(obj=self, response=response)

        response = self.client.post(category.get_absolute_url(),
                                    json.dumps(dict_values),
                                    content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = dict()
        context['products'] = [product.get_values() for product in products]
        self.assertJSONEqual(json.dumps(context), response.content)

    def test_page_category_sorting_buttons(self):
        test_catalogue.create_product_bulk()
        category = Category.objects.get(name='Category-12')

        dict_values = {'page': 1, 'sorting_type': 'popularity', 'num_queries': 20,
                       'filter_slug': 'dlina_1100'}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_ascending', 'num_queries': 20,
                       'filter_slug': 'dlina_1100'}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'num_queries': 20, 'filter_slug': 'dlina_1100'}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20,
                       'filter_slug': 'dlina_1100'}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 3, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

        dict_values = {'page': 4, 'sorting_type': 'price_ascending', 'num_queries': 20}
        self.assertions_sorting_buttons(category=category, dict_values=dict_values)

    def assertions_sorting_buttons(self, category, dict_values={}):
        response = self.client.get(category.get_absolute_url(dict_values), dict_values)
        sort_types = [('popularity', _('By popularity')), ('price_descending', _('By price descending')),
                      ('price_ascending', _('By price ascending'))]

        dict_values['sorting_type'] = dict_values.get('sorting_type', sort_types[0][0])
        for link, text in sort_types:
            if dict_values['sorting_type'] == link:
                sorting_url = '{}?sorting_type={}'.format(category.get_absolute_url(dict_values), link)
                self.assertContains(response,
                                    '<a class="btn btn-default btn-danger" type="button" href="{0}">{1}</a>'.format(
                                        sorting_url, text), count=1, html=True)

    def test_filter_click(self):
        test_catalogue.create_product_bulk()
        category = Category.objects.get(name='Category-12')
        # category = Category.objects.get(name='Category-321')

        dict_values = {'page': 1, 'num_queries': 20, 'filter_slug': 'dlina_1100'}
        self.assertions_filter_click(category=category, dict_values=dict_values)
        self.assertions_filter_remove_click(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_ascending', 'num_queries': 20, 'filter_slug': 'dlina_1100'}
        self.assertions_filter_click(category=category, dict_values=dict_values)
        self.assertions_filter_remove_click(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20, 'filter_slug': 'dlina_1100'}
        self.assertions_filter_click(category=category, dict_values=dict_values)
        self.assertions_filter_remove_click(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'popularity', 'num_queries': 20, 'filter_slug': 'dlina_1100'}
        self.assertions_filter_click(category=category, dict_values=dict_values)
        self.assertions_filter_remove_click(category=category, dict_values=dict_values)

    def assertions_filter_click(self, category, dict_values={}):
        response = self.client.get(category.get_absolute_url())

        # count_products = Filter.objects.filter(slug=dict_values['filter_slug']).first().products.count()
        filters = Feature.objects.filter(slug=dict_values['filter_slug'], filter_products__in=Product.objects.filter(enable=True, categories__in=[category])).annotate(num_prod=Count('filter_products'))
        count_products = filters[0].num_prod

        filter_url = '{}?sorting_type={}'.format(category.get_absolute_url(dict_values), 'popularity')
        self.assertContains(response, '''<a href="{}">
        <input type="checkbox"/>
        длина_1100
        <span class="count">({})</span>
        </a>'''.format(filter_url, count_products), count=1, html=True)

    def assertions_filter_remove_click(self, category, dict_values={}):
        response = self.client.get(category.get_absolute_url(dict_values))

        filters = Feature.objects.filter(slug=dict_values['filter_slug'], filter_products__in=Product.objects.filter(enable=True, categories__in=[category])).annotate(num_prod=Count('filter_products'))
        count_products = filters[0].num_prod

        # filter_url = '{}?sorting_type={}'.format(category.get_absolute_url(), dict_values['sorting_type'])
        filter_url = '{}?sorting_type={}'.format(category.get_absolute_url(), 'popularity')

        self.assertContains(response, '''<a href="{}">
        <input type="checkbox" checked/>
        длина_1100
        <span class="count">({})</span>
        </a>'''.format(filter_url, count_products), count=1, html=True)

    def test_filters_concatenation(self):
        test_catalogue.create_product_bulk()
        category = Category.objects.get(name='Category-12')
        filter = Feature.objects.get(slug='shirina_1000')

        # without filter slugs
        filter_slugs = ''
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        # with one filter in filter slugs
        filter_slugs = 'shirina_1100'
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        # with many filters in filter slugs
        filter_slugs = 'shirina_1100/shirina_1200/shirina_1300/dlina_1000/dlina_1200'
        self.assertions_filter_concatenate(category, filter_slugs, filter)

    def assertions_filter_concatenate(self, category, filter_slugs, filter):
        link_concatenate = concatenate(category, filter_slugs, filter)
        if filter_slugs:
            filter_slugs = filter_slugs.split('/')
        else:
            filter_slugs = []
        if filter.get_absolute_url() in filter_slugs:
            filter_slugs.remove(filter.get_absolute_url())
        else:
            filter_slugs.append(filter.get_absolute_url())
        filter_slugs = '/'.join((filter_slugs))
        absolute_url = category.get_absolute_url({'filter_slug': filter_slugs})
        self.assertEqual(absolute_url, link_concatenate)

    def test_product_options(self):
        test_catalogue.create_product_bulk()

        product1 = Product.objects.get(slug='product-1')
        product2 = Product.objects.get(slug='product-2')

        test_catalogue.create_options(product1, product2)

        response = self.client.get(product1.get_absolute_url())
        options = Feature.objects.filter(Q(level=0), Q(product_options__product=product1) | Q(children__product_options__product=product1)).distinct()

        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(len(options), len(response.context['options']))
        self.assertListEqual(list(options), list(response.context['options']))

    def test_product_options_selenium(self):
        """
        product options selenium test
        """
        test_catalogue.create_product_bulk()

        product1 = Product.objects.get(pk=1)
        product2 = Product.objects.get(pk=2)

        test_catalogue.create_options(product1, product2)

        self.firefox.get(
            '%s%s' % (self.live_server_url,  product1.get_absolute_url())
        )

        # TODO check when we will have price
        price_without_options = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
        if len(price_without_options) == 0:
            raise Exception("price can't be empty")
        self.assertIn("Product 1", self.firefox.title)

        options_db = [option.title for option in Feature.objects.filter(Q(level=0), Q(product_options__product=product1) | Q(children__product_options__product=product1)).distinct()]
        options_on_page = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select").text.split('\n')[1:]
        self.assertListEqual(options_db, options_on_page)

        option1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select/option[4]")
        option1.click()

        # TODO check when price will depend on selected option
        price_option1 = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
        # if price_without_options == price_option1:
        #     self.assertNotEqual(price_without_options, price_option1)

        # parent = Feature.objects.get(title=options_db[0])
        # options_db_level1 = [option.title for option in Feature.objects.filter(level=1, parent=parent.pk)]
        # options_on_page_level1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div[2]/div[2]/div/label/select/option[2]").text
