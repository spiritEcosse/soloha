# --coding: utf-8--

from django.test import TestCase
from django.test import Client
from oscar.core.loading import get_class, get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import IMAGE_NOT_FOUND
from oscar.test import factories
from django.utils.html import strip_entities
from django.core.urlresolvers import reverse
import json
from django.db.models.query import Prefetch
from apps.catalogue.views import ProductCategoryView, ProductDetailView
from django.core.paginator import Paginator
from django.db.models import Count
from python_test.factories import catalogue
from templatetags.filters_concatenation import concatenate
from django.utils.translation import ugettext_lazy as _
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE
from django.db import IntegrityError
import functools
from oscar.apps.partner.strategy import Selector
from selenium.webdriver.support.select import Select
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from django.test import LiveServerTestCase
from django.core import serializers
from django.db.models import Q

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'ProductCategory')
Feature = get_model('catalogue', 'Feature')
test_catalogue = catalogue.Test()

STATUS_CODE_200 = 200


class TestCatalog(TestCase, LiveServerTestCase):
    def setUp(self):
        self.client = Client()
        self.firefox = webdriver.Firefox()
        self.firefox.maximize_window()
        super(TestCatalog, self).setUp()

    def tearDown(self):
        self.firefox.quit()
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
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        product = Product.objects.get(title='Product 20')
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        product = Product.objects.get(title='Product 39')
        response = self.client.get(product.get_absolute_url())
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())

        # attributes = AttributeOptionGroup.objects.filter(productattribute__product__parent=product).prefetch_related(
        #     Prefetch('options',
        #              queryset=AttributeOption.objects.filter(productattributevalue__product__parent=product).distinct(),
        #              to_attr='attr_val')
        # ).distinct()
        test_catalogue.test_menu_categories(obj=self, response=response)

    def test_page_product_attributes_selenium(self):
        """
        test page product with attributes by selenium
        :return:
        """
        only = ['title', 'pk', 'slug']
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        test_catalogue.create_attributes(product)
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(product)

        if info.availability.is_available_to_buy:
            expect_price = str(info.stockrecord.incl_tax)
        else:
            expect_price = _('Product is not available.')

        attributes = Feature.objects.only(*only).filter(children__product_versions__product=product, level=0).prefetch_related(
            Prefetch('children', queryset=Feature.objects.only(*only).filter(level=1, product_versions__product=product).distinct(), to_attr='values')
        ).distinct()

        self.firefox.get('%s%s' % (self.live_server_url, product.get_absolute_url()))
        price = self.firefox.find_element_by_css_selector('div#section3 .price .wrapper-number span').text
        self.assertEqual(price, expect_price)
        attribute_1 = self.firefox.find_element_by_css_selector('.options .panel-default:nth-child(3)')

        expect_attribute_1 = attributes[1]
        attribute_1_name = attribute_1.find_element_by_css_selector('.name').text
        self.assertEqual(attribute_1_name, expect_attribute_1.title)
        attribute_1_values = attribute_1.find_element_by_css_selector('select')
        self.assertListEqual(attribute_1_values.text.split('\n'), [value.title for value in expect_attribute_1.values])
        Select(attribute_1_values).select_by_value('{}'.format(expect_attribute_1.values[2].pk))
        time.sleep(5)

    def test_get_product_attributes(self):
        test_catalogue.create_product_bulk()
        product = Product.objects.get(slug='product-1')
        test_catalogue.create_attributes(product)
        response = self.client.get(product.get_absolute_url())

        attributes = Feature.objects.filter(children__product_versions__product=product, level=0).prefetch_related(
            Prefetch('children', queryset=Feature.objects.filter(level=1, product_versions__product=product).distinct(), to_attr='values')
        ).distinct()
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.resolver_match.func.__name__, ProductDetailView.as_view().__name__)
        self.assertTemplateUsed(response, 'catalogue/detail.html')
        self.assertEqual(response.request['PATH_INFO'], product.get_absolute_url())
        self.assertEqual(product, response.context['product'])
        self.assertEqual(len(attributes), len(response.context['attributes']))
        self.assertListEqual(list(attributes), list(response.context['attributes']))
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

    def tearDown(self):
        # Call tearDown to close the web browser
        self.firefox.quit()
        super(TestCatalog, self).tearDown()

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

        # price_without_options = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
        price_without_options = self.firefox.find_element_by_xpath(".//*[@id='section3']/div[1]/div[1]/div/div[2]/div[1]/span").text
        time.sleep(10)
        if len(price_without_options) == 0:
            raise Exception("price can't be empty")
        self.assertIn("Product 1", self.firefox.title)

        options_db = [option.title for option in Feature.objects.filter(Q(level=0), Q(product_options__product=product1) | Q(children__product_options__product=product1)).distinct()]
        options_on_page = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select").text.split('\n')[1:]
        self.assertListEqual(options_db, options_on_page)

        option1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div/div/label/select/option[4]")
        option1.click()

        price_option1 = self.firefox.find_element_by_xpath(".//*[@id='section3']/div/div[1]/div/div[2]/div[1]/span").text
        if price_without_options == price_option1:
            self.assertNotEqual(price_without_options, price_option1)

        # parent = Feature.objects.get(title=options_db[0])
        # options_db_level1 = [option.title for option in Feature.objects.filter(level=1, parent=parent.pk)]
        # options_on_page_level1 = self.firefox.find_element_by_xpath(".//*[@id='options']/div[2]/div[2]/div[2]/div/label/select/option[2]").text






