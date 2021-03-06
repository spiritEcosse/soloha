
import json
import random
from decimal import Decimal as D
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Min, Sum, Count
from django.db.models import Q
from django.db.models.query import Prefetch
from django.test import Client
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from oscar.apps.partner.strategy import Selector
from oscar.core.loading import get_model
from oscar.test import factories
from selenium.webdriver.support.select import Select
from apps.catalogue.views import ProductCategoryView, ProductDetailView
from python_test.factories import catalogue
from soloha import settings
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from templatetags.filters_concatenation import concatenate
import time
from selenium import webdriver
from django.test import LiveServerTestCase
from django.db.models import Q, F
from haystack.query import SearchQuerySet
from apps.contacts.views import FeedbackForm
from apps.catalogue.models import SiteInfo
from apps.catalogue.views import NOT_SELECTED
from soloha.settings import TEST_INDEX
from django.test import TestCase, override_settings
from django.core.management import call_command
from django.contrib.auth.models import User
from selenium.common.exceptions import NoSuchElementException
from apps.ex_flatpages.models import InfoPage
import haystack
from pyvirtualdisplay import Display

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductOptions = get_model('catalogue', 'ProductOptions')
VersionAttribute = get_model('catalogue', 'VersionAttribute')
ProductCategory = get_model('catalogue', 'ProductCategory')
ProductVersion = get_model('catalogue', 'ProductVersion')
Feature = get_model('catalogue', 'Feature')
WishList = get_model('wishlists', 'WishList')
test_catalogue = catalogue.Test()

STATUS_CODE_200 = 200


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class TestCatalog(LiveServerTestCase):
    css_selector_product_price = 'div#section3 .price .wrapper-number .number'
    css_selector_attribute = '.options .panel-default:nth-child({})'
    start_option = [{'pk': 0, 'title': NOT_SELECTED}]

    def setUp(self):
        self.client = Client()
        self.display = Display(visible=0, size=(1024, 768))
        self.display.start()
        self.firefox = webdriver.Firefox()
        self.firefox.maximize_window()
        super(TestCatalog, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        time.sleep(2)
        self.firefox.quit()
        self.display.stop()
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
                if attribute.price_retail is not None:
                    price += attribute.price_retail
            context['price'] = price
            context['currency'] = settings.OSCAR_DEFAULT_CURRENCY
        return context

    def get_attributes_for_attribute(self, product, attribute):
        only = ['pk', 'title']

        values_in_group = Feature.objects.only(*only).filter(
            level=1, product_versions__product=product, product_versions__attributes=attribute
        )

        attributes = Feature.objects.only(*only).filter(
            children__product_versions__product=product, level=0
        ).prefetch_related(
            Prefetch('children', queryset=values_in_group.annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values_in_group'),
            Prefetch('children', queryset=Feature.objects.only(*only).filter(
                level=1, product_versions__product=product
            ).exclude(
                version_attributes__attribute__in=values_in_group.order_by().distinct()
            ).annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values_out_group')
        ).annotate(
            price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)
        ).order_by('price', '-count_child', 'title', 'pk')

        first = ProductVersion.objects.filter(product=product).annotate(
            price_common=Sum('version_attributes__price_retail') + F('price_retail')
        ).filter(attributes=attribute).order_by('price_common').first()

        attributes = sorted(attributes,
                            key=lambda attr: attr.product_features.filter(product=product).first().sort
                            if attr.product_features.filter(product=product).first() else 0)

        for attr in attributes:
            for val in attr.values_in_group:
                val.prices = []
                val.visible = val in first.attributes.all()

                for prod_ver in val.product_versions.filter(attributes=val, product=product).filter(
                        attributes=attribute):
                    price = ProductVersion.objects.filter(pk=prod_ver.pk).aggregate(
                        common=Sum('version_attributes__price_retail'))
                    price['common'] += prod_ver.price_retail
                    val.prices.append(price['common'])
            attr.values_in_group = sorted(attr.values_in_group, key=lambda val: min(val.prices))
            attr.values = attr.values_in_group + list(attr.values_out_group)

        return attributes

    def get_dict_product_version_price(self, product):
        product_versions = dict()

        for product_version in self.get_product_version(product=product):
            attribute_values = []
            price = product_version.price_retail
            version_attributes = product_version.version_attributes.filter(
                attribute__parent__children__product_versions__product=product, attribute__level=1,
                attribute__parent__level=0
            ).annotate(
                price=Min('version__price_retail'),
                count_child=Count('attribute__parent__children', distinct=True)
            ).order_by('price', '-count_child', 'attribute__parent__title', 'attribute__parent__pk')

            for version_attribute in version_attributes:
                attribute_values.append(version_attribute.attribute)
                if version_attribute.price_retail is not None:
                    price += version_attribute.price_retail
            attribute_values = sorted(attribute_values,
                                      key=lambda attr: attr.product_features.filter(
                                          product=product).first().sort
                                      if attr.product_features.filter(product=product).first() else 0)
            attribute_values = [str(val.pk) for val in attribute_values]
            product_versions[','.join(attribute_values)] = str(price)
        return product_versions

    def test_product_post(self):
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        self.assert_product_post(product=product)

        product = factories.create_product(slug='product-attributes', title='Product attributes', price=5)
        test_catalogue.create_dynamic_attributes(product)
        self.assert_product_post(product=product)

    def get_product_attribute_values(self, product):
        only = ['pk']
        return Feature.objects.only(*only).filter(level=1, product_versions__product=product).distinct()

    def assert_product_post(self, product):
        response = self.client.post(product.get_absolute_url(), content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        context = json.loads(response.content)

        expected_context = dict()
        expected_context['product_versions'] = self.get_dict_product_version_price(product=product)
        expected_context['attributes'] = []
        expected_context['variant_attributes'] = {}

        for attr in self.get_product_attributes(product=product):
            attr.values = self.start_option + map(lambda val: val.get_values(('pk', 'title')), attr.values)
            expected_context['attributes'].append(attr.get_values(('pk', 'title', 'values')))

        for attribute in self.get_product_attribute_values(product):
            attributes = []

            for attr in self.get_attributes_for_attribute(product, attribute):
                values_in_group = self.start_option + map(lambda val: val.get_values(('pk', 'title', 'visible')), attr.values_in_group)

                attributes.append({
                    'pk': attr.pk,
                    'title': attr.title,
                    'in_group': values_in_group,
                    'values': values_in_group + map(lambda val: val.get_values(('pk', 'title')), attr.values_out_group),
                })

            expected_context['variant_attributes'][attribute.pk] = attributes

        self.assertDictEqual(context['product_versions'], expected_context['product_versions'])
        self.assertListEqual(context['attributes'], expected_context['attributes'])
        self.assertDictEqual(expected_context['variant_attributes'], context['variant_attributes'])

    def get_product_attributes(self, product):
        only = ['title', 'pk']
        attributes = Feature.objects.only(*only).filter(
            children__product_versions__product=product, level=0
        ).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*only).filter(
                level=1, product_versions__product=product
            ).annotate(
                price=Min('product_versions__price_retail')
            ).order_by('price', 'title', 'pk'), to_attr='values')
        ).annotate(price=Min('children__product_versions__price_retail'), count_child=Count('children', distinct=True)).\
            order_by('price', '-count_child', 'title', 'pk')

        attributes = sorted(attributes,
                            key=lambda attr: attr.product_features.filter(product=product).first().sort
                            if attr.product_features.filter(product=product).first() else 0)
        return attributes

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
        time.sleep(2)
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(price, str(context['price']))
        self.assertEqual(price, str(D('112.20')))

    def test_page_product_attributes_selenium(self):
        """
        test page product with attributes by selenium
        :return:
        """
        test_catalogue.create_product_bulk()
        product = factories.create_product(slug='product-attributes', title='Product attributes', price=5)
        test_catalogue.create_dynamic_attributes(product)
        attributes = list(self.get_product_attributes(product=product))

        product_versions = self.get_dict_product_version_price(product=product)
        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))

        start_price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        context = self.get_product_price(product=product)
        self.assertEqual(start_price, str(context['price']))
        self.assertEqual(str(D('2100.00')), start_price)

        feature_11 = Feature.objects.get(title='Feature 11')
        feature_21 = Feature.objects.get(title='Feature 21')
        feature_22 = Feature.objects.get(title='Feature 22')
        feature_31 = Feature.objects.get(title='Feature 31')
        feature_32 = Feature.objects.get(title='Feature 32')
        feature_33 = Feature.objects.get(title='Feature 33')
        feature_41 = Feature.objects.get(title='Feature 41')

        attribute = feature_32
        price_11_22_32 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                   product_versions=product_versions)
        self.assertEqual(str(D('2500.00')), price_11_22_32)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_33
        price_11_22_33 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                   product_versions=product_versions)
        self.assertEqual(str(D('2700.00')), price_11_22_33)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_21
        price_11_21_33 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                   product_versions=product_versions)
        self.assertEqual(str(D('2300.00')), price_11_21_33)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_41
        price_11_21_32_41 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                      product_versions=product_versions)
        self.assertEqual(str(D('4310.10')), price_11_21_32_41)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_31
        price_11_21_31 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                   product_versions=product_versions)
        self.assertEqual(str(D('2100.00')), price_11_21_31)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_22
        price_11_22_31 = self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                                   product_versions=product_versions)
        self.assertEqual(str(D('2400.00')), price_11_22_31)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_21
        self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                  product_versions=product_versions,
                                                  earlier_price=price_11_21_31)

        self.assertEqual(str(D('2100.00')), price_11_21_31)

        attributes = list(self.get_attributes_for_attribute(product, attribute))
        attribute = feature_32
        self.checkout_price_by_selected_attribute(attribute=attribute, attributes=attributes,
                                                  product_versions=product_versions,
                                                  earlier_price=price_11_22_32)
        self.assertEqual(str(D('2500.00')), price_11_22_32)

    def checkout_price_by_selected_attribute(self, attribute, attributes, product_versions, earlier_price=None):
        index_attr = attributes.index(attribute.parent)
        expect_attribute = attributes[index_attr]
        attribute_1 = self.firefox.find_element_by_css_selector(self.css_selector_attribute.format(index_attr + 1))
        self.assertEqual(attribute_1.find_element_by_css_selector('.name').text, expect_attribute.title)
        print 'name - {}'.format(expect_attribute.title)
        print expect_attribute.values

        attribute_1.find_element_by_css_selector('button').click()
        attribute_1_values = attribute_1.find_element_by_css_selector('.dropdown-menu')
        self.assertEqual(attribute_1_values.is_displayed(), True)
        self.assertListEqual(attribute_1_values.text.split('\n'), [NOT_SELECTED] + [value.title for value in expect_attribute.values])

        index_attr_val = expect_attribute.values.index(attribute)
        print 'li.list:nth-child({})'.format(index_attr_val + 3)

        time.sleep(2)
        self.assertEqual(attribute_1_values.is_displayed(), True)
        attribute_1_values.find_element_by_css_selector('li.list:nth-child({})'.format(index_attr_val + 3)).click()
        time.sleep(2)

        selected_values = []
        for num in xrange(1, len(attributes) + 1):
            selected = int(self.firefox.find_element_by_css_selector(
                '%s button .attr-pk' % self.css_selector_attribute.format(num)
            ).get_attribute('innerHTML'))

            if selected != 0:
                selected_values.append(selected)

        expected_price = product_versions.get(','.join(map(str, selected_values)))
        price = self.firefox.find_element_by_css_selector(self.css_selector_product_price).text
        self.assertEqual(price, str(expected_price))

        if earlier_price is not None:
            self.assertEqual(price, earlier_price)

        attribute_1.find_element_by_css_selector('button').click()
        return price

    def test_get_product_attributes(self):
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        response = self.client.get(product.get_absolute_url())

        attributes = self.get_product_attributes(product=product)
        self.assertListEqual(attributes, response.context['attributes'])
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
        dict_values = {'page': 1, 'num_queries': 10}
        category = Category.objects.get(name='Category-2')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this child category are not the descendants of the categories at the same time, this category has itself in goods
        # Todo: why 24 queries ?
        dict_values = {'page': 1, 'num_queries': 24}
        category = Category.objects.get(name='Category-321')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this category has category of descendants with itself, this category is not in goods, but its descendants have in the goods
        dict_values = {'page': 1, 'num_queries': 20}
        category = Category.objects.get(name='Category-1')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products with this main category has no descendants of categories at the same time, this category has itself in goods
        dict_values = {'page': 1, 'num_queries': 18}
        category = Category.objects.get(name='Category-4')
        self.assertions_category(category=category, dict_values=dict_values)

        # with products in this category is that the main categories of the children with this very category and its descendants have in the goods
        dict_values = {'page': 1, 'num_queries': 18}
        category = Category.objects.get(name='Category-3')
        self.assertions_category(category=category, dict_values=dict_values)

    def test_page_category_paginator(self):
        test_catalogue.create_product_bulk()

        dict_values = {'page': 1, 'num_queries': 20}
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
        # only = ['title', 'slug', 'structure', 'product_class', 'enable', 'categories', 'filters']
        only = ['title', 'slug', 'structure', 'product_class', 'categories']
        dict_filter = {'enable': True, 'categories__in': category.get_descendants(include_self=True)}

        response = self.client.get(category.get_absolute_url(), dict_values)

        if dict_values.get('filter_slug'):
            dict_filter['filters__slug__in'] = dict_values.get('filter_slug').split('/')

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
        context['products'] = []
        for product in products[OSCAR_PRODUCTS_PER_PAGE*(int(dict_values['page'])-1):OSCAR_PRODUCTS_PER_PAGE*(int(dict_values['page']))]:
            product_values = product.get_values()
            product_values['id'] = product.id
            context['products'].append(product_values)
        content = json.loads(response.content)
        self.assertListEqual(context['products'], content['products'])

    def test_feature_get_values(self):
        """
        test get_values from model Feature
        :return:
        """
        feature = Feature.objects.create(title='Feature 1')
        real_data = feature.get_values(('pk', ))
        expected = {'pk': feature.pk}
        self.assertDictEqual(expected, real_data)

        real_data = feature.get_values(('pk', 'title', 'slug'))
        expected = {'pk': feature.pk, 'title': feature.title, 'slug': feature.slug}
        self.assertDictEqual(expected, real_data)

        real_data = feature.get_values(())
        expected = {}
        self.assertDictEqual(expected, real_data)

    def test_get_values_by_name_field(self):
        """
        test get_data from model Product
        :return:
        """
        product = factories.create_product(title='Product_1')
        real_data = product.get_data(['pk'])
        expected = {'pk': product.pk}
        self.assertDictEqual(expected, real_data)

        real_data = product.get_data(['pk', 'title', 'slug'])
        expected = {'pk': product.pk, 'title': product.title, 'slug': product.slug}
        self.assertDictEqual(expected, real_data)

        real_data = product.get_data([])
        expected = {}
        self.assertDictEqual(expected, real_data)

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
        self.assertContains(response, u'''<a href="{}">
        <input type="checkbox" onclick="location.href='/category-1/category-12/filter/dlina_1100/?sorting_type=popularity'"/>
        длина_1100
        <span class="count">({})</span>
        </a>'''.format(filter_url, count_products), count=1, html=True)

    def assertions_filter_remove_click(self, category, dict_values={}):
        response = self.client.get(category.get_absolute_url(dict_values))

        filters = Feature.objects.filter(slug=dict_values['filter_slug'], filter_products__in=Product.objects.filter(enable=True, categories__in=[category])).annotate(num_prod=Count('filter_products'))
        count_products = filters[0].num_prod

        # filter_url = '{}?sorting_type={}'.format(category.get_absolute_url(), dict_values['sorting_type'])
        filter_url = '{}?sorting_type={}'.format(category.get_absolute_url(), 'popularity')

        self.assertContains(response, u'''<a href="{}">
        <input type="checkbox"  onclick="location.href='/category-1/category-12/?sorting_type=popularity'" checked/>
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
        # tests filtering on page with search results, on this page category empty
        category = ''
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        # with one filter in filter slugs
        filter_slugs = 'shirina_1100'
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        category = ''
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        # with many filters in filter slugs
        filter_slugs = 'shirina_1100/shirina_1200/shirina_1300/dlina_1000/dlina_1200'
        self.assertions_filter_concatenate(category, filter_slugs, filter)

        category = ''
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

        if category:
            absolute_url = category.get_absolute_url({'filter_slug': filter_slugs})
        else:
            if filter_slugs and ('filter/' not in filter_slugs):
                absolute_url = '/search/filter/' + filter_slugs + '/'
            elif filter_slugs:
                absolute_url = filter_slugs + '/'
            else:
                absolute_url = '/search/'
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

    # def test_product_options_selenium(self):
    #     """
    #     product options selenium test
    #     """
    #     test_catalogue.create_product_bulk()
    #
    #     product1 = Product.objects.get(pk=1)
    #     product2 = Product.objects.get(pk=2)
    #
    #     test_catalogue.create_options(product1, product2)
    #
    #     self.firefox.get(
    #         '%s%s' % (self.live_server_url,  product1.get_absolute_url())
    #     )
    #
    #     # TODO check when we will have price
    #     price_without_options = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
    #     if len(price_without_options) == 0:
    #         raise Exception("price can't be empty")
    #     self.assertIn("Product 1", self.firefox.title)
    #
    #     options_db = [option.title for option in Feature.objects.filter(Q(level=0), Q(product_options__product=product1) | Q(children__product_options__product=product1)).distinct()]
    #     options_on_page = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select").text.split('\n')[1:]
    #     self.assertListEqual(options_db, options_on_page)
    #
    #     option1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select/option[4]")
    #     option1.click()
    #
    #     price_option1 = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
    #     if price_without_options == price_option1:
    #         self.assertNotEqual(price_without_options, price_option1)

        # parent = Feature.objects.get(title=options_db[0])
        # options_db_level1 = [option.title for option in Feature.objects.filter(level=1, parent=parent.pk)]
        # options_on_page_level1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div[2]/div[2]/div/label/select/option[2]").text

    def test_product_search(self):
        #ToDo add case with filters and (filters, page)
        test_catalogue.create_product_bulk()

        # Searching products starting from Product 1
        dict_values = {'search_string': 'Product 1', 'page': 1}
        self.assertions_product_search(dict_values=dict_values)

        # Searching many products with similar names
        dict_values = {'search_string': 'Product', 'page': 1}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'Product', 'page': 2}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': '', 'page': 1}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': '1', 'page': 1}
        self.assertions_product_search(dict_values=dict_values)

    def test_product_search_sorting_with_filters(self):
        test_catalogue.create_product_bulk()

        dict_values = {'search_string': 'product', 'page': 1, 'sorting_type': 'price_ascending', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'page': 2, 'sorting_type': 'popularity', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20, 'filters': ''}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'page': 1, 'sorting_type': 'price_descending', 'num_queries': 20,
                       'filters': 'shirina_1000/shirina_1100/shirina_1200/dlina_1000/dlina_1100'}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'page': 2, 'sorting_type': 'popularity', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_product_search(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'page': 1, 'sorting_type': 'popularity', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_product_search(dict_values=dict_values)

    def assertions_product_search(self, dict_values=None):
        paginate_by = OSCAR_PRODUCTS_PER_PAGE
        dict_filter = dict()

        if dict_values.get('filter_slug'):
            dict_filter['filters__slug__in'] = dict_values.get('filter_slug').split('/')

        dict_new_sorting_types = {'popularity': '-views_count', 'price_ascending': 'stockrecords__price_excl_tax',
                'price_descending': '-stockrecords__price_excl_tax'}
        dict_values['sorting_type'] = dict_new_sorting_types.get(dict_values.get('sorting_type'), '-views_count')

        response = self.client.get('/search/?q={}'.format(dict_values['search_string']))
        sqs_search = self.get_search_queryset(dict_values=dict_values)

        searched_products = [{'id': obj.pk,
                              'title': obj.title,
                              'main_image': obj.object.get_values()['image'],
                              'href': obj.object.get_absolute_url(),
                              'price': obj.object.get_values()['price']} for obj in sqs_search]

        products_pk = [product.pk for product in sqs_search]
        dict_filter['id__in'] = products_pk
        products_without_filters = Product.objects.only('id').filter(id__in=products_pk).distinct().order_by(
            dict_values.get('sorting_type'))
        queryset_filters = Feature.objects.filter(filter_products__in=products_without_filters).distinct().prefetch_related('filter_products')
        filters = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters, to_attr='children_in_products'),
        ).distinct()

        response_titles = [product.title for product in list(response.context['page_obj'])]
        products_titles = [product['title'] for product in searched_products][:OSCAR_PRODUCTS_PER_PAGE]
        p = Paginator(searched_products, paginate_by)

        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(len(p.page(dict_values.get('page', 1)).object_list), len(response.context['page_obj']))
        self.assertListEqual(products_titles, response_titles)
        self.assertTemplateUsed(response, 'search/results.html')
        self.assertEqual(p.count, response.context['paginator'].count)
        self.assertEqual(p.num_pages, response.context['paginator'].num_pages)
        self.assertEqual(p.page_range, response.context['paginator'].page_range)
        self.assertEqual(list(filters), list(response.context['filters']))

        response = self.client.post('http://localhost:8000/search/?q={}/'.format(dict_values.get('search_string', '')),
                                    json.dumps(dict_values),
                                    content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        context = dict()
        sqs = self.get_search_queryset(dict_values=dict_values)
        context['searched_products'] = [{'id': int(obj.pk),
                              'title': obj.title,
                              'image': obj.object.get_values()['image'],
                              'absolute_url': obj.object.get_absolute_url(),
                              'price': obj.object.get_values()['price']} for obj in sqs][OSCAR_PRODUCTS_PER_PAGE*(int(dict_values['page'])-1):OSCAR_PRODUCTS_PER_PAGE*(int(dict_values['page']))]
        content = json.loads(response.content)
        self.assertListEqual(context['searched_products'], content['products'])

    @staticmethod
    def get_search_queryset(dict_values=None):
        sqs_search = []
        if dict_values['search_string']:
            sqs = SearchQuerySet()
            sqs_title = sqs.autocomplete(title_ngrams=dict_values['search_string'])
            sqs_slug = sqs.autocomplete(slug_ngrams=dict_values['search_string'])
            sqs_id = sqs.autocomplete(product_id=dict_values['search_string'])
            sqs_search = (sqs_title or sqs_slug or sqs_id) #[:OSCAR_PRODUCTS_PER_PAGE]
        return sqs_search

    # test input search field in all pages
    def test_product_search_input_selenium(self):
        test_catalogue.create_product_bulk()

        product1 = Product.objects.get(slug='product-1')
        category1 = Category.objects.get(name='Category-1')
        category12 = Category.objects.get(name='Category-12')
        category123 = Category.objects.get(name='Category-123')

        dict_values = {'page_url': ''}
        self.assertions_product_search_input_selenium(dict_values=dict_values)

        dict_values['page_url'] = product1.get_absolute_url()
        self.assertions_product_search_input_selenium(dict_values=dict_values)

        dict_values['page_url'] = category1.get_absolute_url()
        self.assertions_product_search_input_selenium(dict_values=dict_values)

        dict_values['page_url'] = category12.get_absolute_url()
        self.assertions_product_search_input_selenium(dict_values=dict_values)

        dict_values['page_url'] = category123.get_absolute_url()
        self.assertions_product_search_input_selenium(dict_values=dict_values)

        dict_values['page_url'] = '/contacts/'
        self.assertions_product_search_input_selenium(dict_values=dict_values)

    def assertions_product_search_input_selenium(self, dict_values={}):
        self.firefox.get('%s%s' % (self.live_server_url,  dict_values['page_url']))

        search_menu = self.firefox.find_element_by_name('search-menu')
        self.assertEqual(search_menu.is_displayed(), False)

        dict_values = {'search_string': 'product'}
        sqs_search = self.get_search_queryset(dict_values=dict_values)
        list_elements_sqs = [product.title for product in sqs_search[:5]]
        first_product = sqs_search[0].title

        input_field = self.firefox.find_element_by_css_selector(".form-control")
        input_field.send_keys(dict_values['search_string'])
        time.sleep(2)

        popup_first_element = self.firefox.find_element_by_css_selector(
            ".search .dropdown-menu .item:nth-child(1) .title").text
        self.assertEqual(search_menu.is_displayed(), True)
        self.assertNotEqual(len(popup_first_element), 0)
        self.assertEqual(popup_first_element, first_product)

        list_elements_on_page = []
        for i in xrange(1, 6):
            list_elements_on_page.append(self.firefox.find_element_by_css_selector(
                ".search .dropdown-menu .item:nth-child({}) .title".format(i)).text)
        self.assertListEqual(list_elements_on_page, list_elements_sqs)

        input_field.clear()
        self.assertEqual(search_menu.is_displayed(), False)

        input_field.send_keys('product')
        time.sleep(2)
        self.assertEqual(search_menu.is_displayed(), True)

        input_field.send_keys('tt')
        time.sleep(2)
        self.assertEqual(search_menu.is_displayed(), False)

    def test_search_page_sorting_buttons(self):
        test_catalogue.create_product_bulk()

        dict_values = {'search_string': 'product', 'sorting_type': 'popularity',
                       'filter_slug': 'filter/dlina_1100/'}
        self.assertions_search_page_sorting_buttons(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'sorting_type': 'price_ascending',
                       'filter_slug': 'filter/dlina_1100/'}
        self.assertions_search_page_sorting_buttons(dict_values=dict_values)

        dict_values = {'search_string': 'product',  'filter_slug': 'filter/dlina_1100/'}
        self.assertions_search_page_sorting_buttons(dict_values=dict_values)

    def assertions_search_page_sorting_buttons(self, dict_values={}):
        response = self.client.get('/search/{0}?q={1}&sorting_type={2}'.format(dict_values.get('filter_slug', ''),
                                                                               dict_values.get('search_string', ''),
                                                                               dict_values.get('sorting_type', '')))
        sort_types = [('popularity', _('By popularity')), ('price_descending', _('By price descending')),
                      ('price_ascending', _('By price ascending'))]

        dict_values['sorting_type'] = dict_values.get('sorting_type', sort_types[0][0])
        for link, text in sort_types:
            if dict_values['sorting_type'] == link:
                sorting_url = '/search/{0}?q={1}&sorting_type={2}'.format(dict_values.get('filter_slug', ''),
                                                                         dict_values.get('search_string', ''),
                                                                         link)
                self.assertContains(response,
                                    '<a class="btn btn-default btn-danger" type="button" href="{0}">{1}</a>'.format(
                                        sorting_url, text), count=1, html=True)

    def test_filter_click_search_page(self):
        test_catalogue.create_product_bulk()

        dict_values = {'search_string': 'product', 'filter_slug': 'filter/dlina_1100/'}
        self.assertions_filter_click_search_page(dict_values=dict_values)
        self.assertions_filter_remove_click_search_page(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'sorting_type': 'price_ascending', 'filter_slug': 'filter/dlina_1100/'}
        self.assertions_filter_click_search_page(dict_values=dict_values)
        self.assertions_filter_remove_click_search_page(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'sorting_type': 'price_descending', 'filter_slug': 'filter/dlina_1100/'}
        self.assertions_filter_click_search_page(dict_values=dict_values)
        self.assertions_filter_remove_click_search_page(dict_values=dict_values)

        dict_values = {'search_string': 'product', 'sorting_type': 'popularity', 'filter_slug': 'filter/dlina_1100/'}
        self.assertions_filter_click_search_page(dict_values=dict_values)
        self.assertions_filter_remove_click_search_page(dict_values=dict_values)

    def assertions_filter_click_search_page(self, dict_values={}):
        response = self.client.get('/search/?q={0}&sorting_type={1}'.format(dict_values.get('search_string', ''),
                                                                            dict_values.get('sorting_type', '')))

        products_without_filters = Product.objects.all().distinct()
        queryset_filters = Feature.objects.filter(filter_products__in=products_without_filters).distinct().prefetch_related('filter_products')
        filters = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters.annotate(num_prod=Count('filter_products')),
                     to_attr='children_in_products'),
        ).distinct()

        count_products = filters[0].children_in_products[1].num_prod

        filter_url = '/search/{0}?q={1}&sorting_type={2}'.format(dict_values.get('filter_slug', ''),
                                                                 dict_values.get('search_string', ''),
                                                                 dict_values.get('sorting_type', 'popularity'))

        self.assertContains(response, u'''<a href="{}">
        <input type="checkbox" onclick="location.href='/search/filter/dlina_1100/?q=product&sorting_type={}'" value="value" name="checkbox"/>
        длина_1100
        <span class="count">({})</span>
        </a>'''.format(filter_url, dict_values.get('sorting_type', 'popularity'), count_products), count=1, html=True)

    def assertions_filter_remove_click_search_page(self, dict_values={}):
        response = self.client.get('/search/{0}?q={1}&sorting_type={2}'.format(dict_values.get('filter_slug', ''),
                                                                               dict_values.get('search_string', ''),
                                                                               dict_values.get('sorting_type', '')))

        products_without_filters = Product.objects.all().distinct()

        queryset_filters = Feature.objects.filter(filter_products__in=products_without_filters).distinct().prefetch_related('filter_products')
        filters = Feature.objects.filter(level=0, children__in=queryset_filters).prefetch_related(
            Prefetch('children', queryset=queryset_filters.annotate(num_prod=Count('filter_products')),
                     to_attr='children_in_products'),
        ).distinct()

        count_products = filters[0].children_in_products[1].num_prod

        filter_url = '/search/?q={0}&sorting_type={1}'.format(dict_values.get('search_string', ''),
                                                                 dict_values.get('sorting_type', 'popularity'))

        self.assertContains(response, u'''<a href="{}">
        <input type="checkbox"  onclick="location.href='/search/?q=product&sorting_type={}'" checked/>
        длина_1100
        <span class="count">({})</span>
        </a>'''.format(filter_url, dict_values.get('sorting_type', 'popularity'), count_products), count=1, html=True)

    def test_filter_checkbox_selenium(self):
        test_catalogue.create_product_bulk()

        category = Category.objects.get(name='Category-12')

        dict_values = {'search_string': 'product', 'sorting_type': 'popularity'}
        initial_url = ('%s%s' % (self.live_server_url, '/search/?q={0}&sorting_type={1}'.format(dict_values.get('search_string', ''),
                                                                                                dict_values.get('sorting_type', ''))))
        self.assertions_filter_checkbox_selenium(url=initial_url)

        initial_url = ('%s%s%s' % (self.live_server_url, category.get_absolute_url(), '?sorting_type=popularity'))
        self.assertions_filter_checkbox_selenium(url=initial_url)

    def assertions_filter_checkbox_selenium(self, url):
        initial_url = url
        self.firefox.get(initial_url)
        checkbox_unchecked = self.firefox.find_element_by_css_selector(
            ".filter .items .values .list-group-item input")
        self.assertEqual(checkbox_unchecked.is_selected(), False)
        checkbox_unchecked.click()
        time.sleep(2)
        self.assertNotEqual(self.firefox.current_url, initial_url)

        checkbox_checked = self.firefox.find_element_by_css_selector(
            ".filter .items .values .list-group-item input")
        self.assertEqual(checkbox_checked.is_selected(), True)
        checkbox_checked.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)

    def test_form_contacts(self):
        form_data = {'confirmation_key': 1, 'name': 'test', 'phone': '0959999999', 'email': 'wrq@gmail.com', 'comment': 'My comment'}
        form_errors = {}
        self.assertions_form_contacts(form_data=form_data, form_errors=form_errors)

        form_data = {}
        form_errors = {'comment': [u'Please enter your message.'],
                       'confirmation_key': [u'This field is required.'],
                       'email': [u'Please enter your email.']}

        self.assertions_form_contacts(form_data=form_data, form_errors=form_errors)

        form_data = {'confirmation_key': 1, 'email': 'wrq@gmail.com', 'comment': 'My comment'}
        form_errors = {}
        self.assertions_form_contacts(form_data=form_data, form_errors=form_errors)

        form_data = {'confirmation_key': 1, 'email': 'wrq@gmail', 'comment': 'My comment'}
        form_errors = {'email': [u'Enter a valid email address.']}
        self.assertions_form_contacts(form_data=form_data, form_errors=form_errors)

    def assertions_form_contacts(self, form_data={}, form_errors={}):
        form = FeedbackForm(data=form_data)
        self.assertDictEqual(form.errors, form_errors)

    def test_form_contacts_selenium(self):
        self.firefox.get('%s%s' % (self.live_server_url,  '/contacts/'))

        submit_btn = self.firefox.find_element_by_xpath(".//*[@id='comment_form']")
        self.assertFalse(submit_btn.is_enabled())

        dict_values = {'name': 'test', 'phone': '0959999999', 'email': 'wrq@gmail.com', 'comment': 'My comment'}
        input_email = self.firefox.find_element_by_xpath(".//*[@id='id_email']")
        input_comment = self.firefox.find_element_by_xpath(".//*[@id='id_comment']")
        input_email.send_keys(dict_values['email'])
        input_comment.send_keys(dict_values['comment'])
        time.sleep(2)
        self.assertTrue(submit_btn.is_enabled())

        submit_btn.click()
        time.sleep(2)
        alert_message = self.firefox.find_element_by_xpath(".// *[ @ id = 'alerts'] / alert").text
        self.assertEqual(alert_message, 'Your message sent!')

        dict_values['email'] = 'qefqeqwfw'
        dict_values['phone'] = '111111'
        input_email.clear()
        input_phone = self.firefox.find_element_by_xpath(".//*[@id='id_phone']")
        input_email.send_keys(dict_values['email'])
        input_phone.send_keys(dict_values['phone'])
        time.sleep(2)

        email_error = self.firefox.find_element_by_css_selector(".has-feedback:nth-child(5) .invalid:nth-child(2)").text
        phone_error = self.firefox.find_element_by_css_selector(".has-feedback:nth-child(4) .invalid").text
        errors = {'email': 'Enter a valid email address.', 'phone': 'Enter a valid phone number'}
        self.assertEqual(email_error, errors['email'])
        self.assertEqual(phone_error, errors['phone'])
        self.assertFalse(submit_btn.is_enabled())

        #ToDo taras: add test for scroll

    def test_show_more_goods_selenium_search_page(self):
        test_catalogue.create_product_bulk()
        dict_values = {'search_string': 'product'}
        initial_url = ('%s%s' % (self.live_server_url, '/search/?q={0}'.format(dict_values.get('search_string', ''))))
        self.assertions_show_more_goods_search_page_selenium(url=initial_url)

    def assertions_show_more_goods_search_page_selenium(self, url):
        initial_url = url
        self.firefox.get(initial_url)
        time.sleep(3)
        more_goods_button = self.firefox.find_element_by_css_selector(".more_products")
        more_goods_button.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)
        self.assertIn('Product 1', self.firefox.page_source)
        self.assertIn('Product 25', self.firefox.page_source)
        self.assertIn('Product 48', self.firefox.page_source)
        self.assertNotIn('Product 49', self.firefox.page_source)

        paginator_one = self.firefox.find_element_by_css_selector(".pagination li:nth-child(1) a")
        paginator_one.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)

        paginator_two = self.firefox.find_element_by_css_selector(".pagination li:nth-child(2) a")
        paginator_two.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)

        paginator_three = self.firefox.find_element_by_css_selector(".pagination li:nth-child(3) a")
        paginator_three.click()
        time.sleep(2)
        self.assertNotEqual(self.firefox.current_url, initial_url)

        more_goods_button = self.firefox.find_element_by_css_selector(".more_products")
        more_goods_button.click()
        time.sleep(4)
        self.assertIn('Product 49', self.firefox.page_source)
        self.assertNotIn('Product 97', self.firefox.page_source)
        self.assertIn(u'ПОКАЗАТЬ ЕЩЕ', self.firefox.page_source)

        more_goods_button = self.firefox.find_element_by_css_selector(".more_products")
        more_goods_button.click()
        time.sleep(2)
        self.assertIn('Product 118', self.firefox.page_source)
        self.assertIn('ng-hide="hide == true"', self.firefox.page_source)

        self.firefox.get(initial_url+"&page=5")
        time.sleep(2)
        self.assertNotIn(u'ПОКАЗАТЬ ЕЩЕ', self.firefox.page_source)

    def test_show_more_goods_category_page_selenium(self):
        test_catalogue.create_product_bulk()
        category = Category.objects.get(name='Category-12')

        initial_url = ('%s%s%s' % (self.live_server_url, category.get_absolute_url(), '?sorting_type=price_ascending'))
        self.assertions_show_more_goods_category_page_selenium(url=initial_url)

    def assertions_show_more_goods_category_page_selenium(self, url):
        initial_url = url
        self.firefox.get(initial_url)
        time.sleep(3)
        more_goods_button = self.firefox.find_element_by_css_selector(".more_products")
        more_goods_button.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)
        self.assertIn('Product 1', self.firefox.page_source)
        self.assertIn('Product 25', self.firefox.page_source)
        self.assertIn('Product 68', self.firefox.page_source)
        self.assertNotIn('Product 69', self.firefox.page_source)

        paginator_one = self.firefox.find_element_by_css_selector(".pagination li:nth-child(1) a")
        paginator_one.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)

        paginator_two = self.firefox.find_element_by_css_selector(".pagination li:nth-child(2) a")
        paginator_two.click()
        time.sleep(2)
        self.assertEqual(self.firefox.current_url, initial_url)

        paginator_three = self.firefox.find_element_by_css_selector(".pagination li:nth-child(3) a")
        paginator_three.click()
        time.sleep(2)
        self.assertNotEqual(self.firefox.current_url, initial_url)
        self.assertIn(u'ПОКАЗАТЬ ЕЩЕ', self.firefox.page_source)

        more_goods_button = self.firefox.find_element_by_css_selector(".more_products")
        more_goods_button.click()
        time.sleep(2)
        self.assertIn('Product 69', self.firefox.page_source)
        self.assertIn('Product 118', self.firefox.page_source)
        self.assertNotIn('Product 68', self.firefox.page_source)
        self.assertIn('ng-hide="hide == true"', self.firefox.page_source)

        self.firefox.get(initial_url+"&page=4")
        time.sleep(2)
        self.assertNotIn(u'ПОКАЗАТЬ ЕЩЕ', self.firefox.page_source)

    def test_wish_list(self):
        test_catalogue.create_product_bulk()
        product_1 = Product.objects.get(slug='product-1')

        # wish list needs loged in user
        username = 'test'
        email = 'test@test.com'
        password = 'test'
        test_user = User.objects.create_user(username, email, password)
        login = self.client.login(username=username, password=password)
        self.assertEqual(login, True)

        WishList.objects.create(owner=test_user)
        wish_list = self.get_wish_list(owner=test_user)
        wish_list.add(product_1)
        wish_list_url = wish_list.get_absolute_url()
        active = self.check_active_product_in_wish_list(wish_list=wish_list, product_id=product_1.id)

        response = self.client.post(product_1.get_absolute_url(), content_type='application/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        context = json.loads(response.content)

        self.assertEqual(wish_list_url, context['wish_list_url'])
        self.assertEqual(active, context['active'])

    @staticmethod
    def get_wish_list(owner):
        wish_list = WishList.objects.filter(owner=owner).first()
        return wish_list

    @staticmethod
    def check_active_product_in_wish_list(wish_list, product_id):
        product_in_wish_list = 'none'
        if wish_list:
            for line in wish_list.lines.all():
                if product_id == line.product_id:
                    product_in_wish_list = 'active'

        return product_in_wish_list

    def test_wish_list_selenium(self):
        test_catalogue.create_product_bulk()
        product_2 = Product.objects.get(slug='product-2')

        # login user in selenium
        username = 'test'
        email = 'test@test.com'
        password = 'test'
        User.objects.create_superuser(username, email, password)
        self.client.login(username=username, password=password)
        cookie = self.client.cookies['sessionid']
        self.firefox.get(self.live_server_url + '/admin/')
        self.firefox.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.firefox.refresh()
        self.firefox.get('%s%s' % (self.live_server_url, product_2.get_absolute_url()))

        text_wish_list = self.firefox.find_element_by_css_selector(".glyphicon-class").text
        self.assertEqual('Add to wish list', text_wish_list)

        add_to_wish_list_button = self.firefox.find_element_by_css_selector(".glyphicon.glyphicon-heart")
        add_to_wish_list_button.click()
        time.sleep(3)

        text_wish_list = self.firefox.find_element_by_css_selector(".glyphicon-class").text
        self.assertEqual('Remove from wish list', text_wish_list)

    def test_wish_list_selenium_no_login(self):
        test_catalogue.create_product_bulk()
        product_2 = Product.objects.get(slug='product-2')

        self.firefox.get('%s%s' % (self.live_server_url, product_2.get_absolute_url()))
        self.assertIn('Please login to add products to a wish list.', self.firefox.page_source)

    def test_flatpages_selenium(self):
        test_catalogue.create_product_bulk()
        product_2 = Product.objects.get(slug='product-2')

        self.firefox.get('%s%s' % (self.live_server_url, product_2.get_absolute_url()))

        self.assertFalse(self.check_exists_element_on_page(".icon-car"))
        self.assertFalse(self.check_exists_element_on_page(".icon-pay"))
        self.assertFalse(self.check_exists_element_on_page(".icon-manager"))

        test_catalogue.create_flatpages()

        self.firefox.refresh()

        self.assertTrue(self.check_exists_element_on_page(".icon-car"))
        self.assertTrue(self.check_exists_element_on_page(".icon-pay"))
        self.assertTrue(self.check_exists_element_on_page(".icon-manager"))

    def check_exists_element_on_page(self, css):
        try:
            self.firefox.find_element_by_css_selector(css)
        except NoSuchElementException:
            return False
        return True

    def test_flatpages(self):
        test_catalogue.create_product_bulk()
        test_catalogue.create_flatpages()

        product_2 = Product.objects.get(slug='product-2')

        response = self.client.get(product_2.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)

        context = dict()
        context['flatpages'] = self.get_flatpages()
        dict_values = {'url': 'delivery', 'context_test': context['flatpages'], 'response_context': response.context['flatpages']}
        self.assertions_flatpages(dict_values=dict_values)

        dict_values['url'] = 'payment'
        self.assertions_flatpages(dict_values=dict_values)

        dict_values['url'] = 'manager'
        self.assertions_flatpages(dict_values=dict_values)

    @staticmethod
    def get_flatpages():
        context = dict()
        context['delivery'] = InfoPage.objects.filter(url='delivery').first()
        context['payment'] = InfoPage.objects.filter(url='payment').first()
        context['manager'] = InfoPage.objects.filter(url='manager').first()

        return context

    def assertions_flatpages(self, dict_values):
        self.assertEqual(dict_values['context_test'], dict_values['response_context'])
        self.assertEqual(dict_values['context_test'][dict_values['url']].title, dict_values['response_context'][dict_values['url']].title)
        self.assertEqual(dict_values['context_test'][dict_values['url']].content, dict_values['response_context'][dict_values['url']].content)
