# --coding: utf-8--

from django.test import TestCase
from django.test import Client
from oscar.core.loading import get_class, get_model
from oscar.test.factories import create_product
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from easy_thumbnails.files import get_thumbnailer
from soloha.settings import IMAGE_NOT_FOUND
from oscar.test import factories
from django.utils.html import strip_entities
from django.core.urlresolvers import reverse
import json
from django.db.models.query import Prefetch
from apps.catalogue.views import ProductCategoryView, CategoryProducts
from django.core.paginator import Paginator
from test.factories import catalogue
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'ProductCategory')
test_catalogue = catalogue.Test()

STATUS_CODE_200 = 200


class TestCatalog(TestCase):
    def setUp(self):
        self.client = Client()

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

    def test_sorting_products_post(self):
        """
        Test sorting products by popularity, price descending and price ascending
        Returns: sorted products
        """
        test_catalogue.create_product_bulk()

        sorting_dict = {
            'sorting_type': 'stockrecords__price_excl_tax',
            # 'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'
        }
        sorting_dict['filters'] = 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        sorting_dict['filters'] = 'shirina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        # sorting_dict['filters'] = ''
        self.assertions_sorting(sorting_dict=sorting_dict)

        sorting_dict['sorting_type'] = '-stockrecords__price_excl_tax'
        sorting_dict['filters'] = 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        sorting_dict['filters'] = 'shirina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        # sorting_dict['filters'] = ''
        self.assertions_sorting(sorting_dict=sorting_dict)

        sorting_dict['sorting_type'] = 'rating'
        sorting_dict['filters'] = 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        sorting_dict['filters'] = 'shirina_1000'
        self.assertions_sorting(sorting_dict=sorting_dict)
        # sorting_dict['filters'] = ''
        self.assertions_sorting(sorting_dict=sorting_dict)

    def assertions_sorting(self, sorting_dict={}):
        paginate_by = OSCAR_PRODUCTS_PER_PAGE
        # sorting_dict = {
        #     'sorting_type': 'stockrecords__price_excl_tax',
        #     'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'
        # }

        # with self.assertNumQueries(10):
        response = self.client.post(reverse('catalogue:products'),
                                    json.dumps(sorting_dict),
                                    content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, response.status_code)
        object_list = Product.objects
        if sorting_dict.get('filters', False) is not False:
            object_list = object_list.filter(filters__slug__in=sorting_dict['filters'].split('/'))

        object_list = object_list.select_related(
            'product_class').prefetch_related(
            Prefetch('categories'),
            Prefetch('images'),
            Prefetch('stockrecords'),
        ).order_by(sorting_dict['sorting_type'])

        context = dict()
        context['products'] = [product.get_values() for product in object_list]
        self.assertJSONEqual(json.dumps(context), response.content)
        p = Paginator(object_list, paginate_by)

        # self.assertEqual(len(p.page(dict_values.get('page', 1)).object_list), len(response.context['page_obj']))
        # self.assertListEqual(list(p.page(dict_values.get('page', 1)).object_list), list(response.context['page_obj']))
        # self.assertEqual(p.count, response.context['paginator'].count)
        # self.assertEqual(p.num_pages, response.context['paginator'].num_pages)
        # self.assertEqual(p.page_range, response.context['paginator'].page_range)


    def test_page_category(self):
        """
        Check the availability of a specific category page template, type the name of the class, true to the object
        of a category, a fixed amount of goods in the different versions of the tree search.
        Returns:
            None
        """
        test_catalogue.create_product_bulk()
        # without products in this category has no descendants in the categories at the same time this very category and its children is not goods
        category = Category.objects.get(name='Category-2')
        self.assertions_category(category=category)

        # with products in this child category are not the descendants of the categories at the same time, this category has itself in goods
        category = Category.objects.get(name='Category-321')
        self.assertions_category(category=category)

        # with products in this category has category of descendants with itself, this category is not in goods, but its descendants have in the goods
        category = Category.objects.get(name='Category-1')
        self.assertions_category(category=category)

        # with products with this main category has no descendants of categories at the same time, this category has itself in goods
        category = Category.objects.get(name='Category-4')
        self.assertions_category(category=category)

        # with products in this category is that the main categories of the children with this very category and its descendants have in the goods
        category = Category.objects.get(name='Category-3')
        self.assertions_category(category=category)

        # check pagination
        category = Category.objects.get(name='Category-1')
        self.assertions_category(category=category)
        dict_values = {'page': 1}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3}
        self.assertions_category(category=category, dict_values=dict_values)

        # Sorted by price ascending
        dict_values = {'page': 1, 'sorting_type': 'stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)
        # TODO use price_retail

        # sorting by price descending
        dict_values = {'page': 1, 'sorting_type': '-stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': '-stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': '-stockrecords__price_excl_tax'}
        self.assertions_category(category=category, dict_values=dict_values)

        # sorting by rating
        dict_values = {'page': 1, 'sorting_type': 'rating'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'rating'}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'rating'}
        self.assertions_category(category=category, dict_values=dict_values)

        # sorting with filters
        dict_values = {'page': 1, 'sorting_type': 'rating', 'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'rating', 'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'rating', 'filters': ''}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'rating', 'filters': 'shirina_1000/shirina_1100/shirina_1200/dlina_1000/dlina_1100'}
        self.assertions_category(category=category, dict_values=dict_values)

        # with page not exist
        # current_page = 200
        # response = self.client.get(category.get_absolute_url(), {'page': current_page})
        # products = Product.objects.filter(enable=True, categories__in=category.get_descendants(include_self=True)).distinct()
        # p = Paginator(products, paginate_by)
        # self.assertEqual(list(p.page(1).object_list), list(response.context['page_obj']))

    def assertions_category(self, category, dict_values={}):
        paginate_by = OSCAR_PRODUCTS_PER_PAGE
        if dict_values.get('filters'):
            dict_filter = {'enable': True, 'categories__in': category.get_descendants(include_self=True),
                           'filters__slug__in': dict_values.get('filters').split('/')}
        else:
            dict_filter = {'enable': True, 'categories__in': category.get_descendants(include_self=True)}

        products = Product.objects.filter(**dict_filter).distinct().order_by(dict_values.get('sorting_type', *Product._meta.ordering))

        response = self.client.get(category.get_absolute_url(), dict_values)

        p = Paginator(products, paginate_by)
        self.assertEqual(response.status_code, STATUS_CODE_200)
        self.assertEqual(response.resolver_match.func.__name__, ProductCategoryView.as_view().__name__)
        self.assertEqual(response.request['PATH_INFO'], category.get_absolute_url())
        self.assertTemplateUsed(response, 'catalogue/category.html')
        self.assertEqual(category, response.context['category'])
        self.assertEqual(len(p.page(dict_values.get('page', 1)).object_list), len(response.context['page_obj']))
        self.assertListEqual(list(p.page(dict_values.get('page', 1)).object_list), list(response.context['page_obj']))
        self.assertEqual(p.count, response.context['paginator'].count)
        self.assertEqual(p.num_pages, response.context['paginator'].num_pages)
        self.assertEqual(p.page_range, response.context['paginator'].page_range)

        test_catalogue.test_menu_categories(obj=self, response=response)
