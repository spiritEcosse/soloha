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
from apps.catalogue.views import ProductCategoryView
from django.core.paginator import Paginator
from test.factories import catalogue
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from soloha.settings import OSCAR_PRODUCTS_PER_PAGE

Product = get_model('catalogue', 'product')
ProductClass = get_model('catalogue', 'ProductClass')
Category = get_model('catalogue', 'category')
ProductCategory = get_model('catalogue', 'ProductCategory')
Filter = get_model('catalogue', 'Filter')
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

        # AttributeOptionGroup.objects.filter(productattribute__product__parent=product).prefetch_related(Prefetch('options', queryset=AttributeOption.objects.filter(productattributevalue__product__parent=product).distinct(), to_attr='attr_val')).distinct()
        # [(attr_opt, [value.productattributevalue_set.first() for value in attr_opt.attr_val]) for attr_opt in AttributeOptionGroup.objects.filter(productattribute__product__parent=product).prefetch_related(Prefetch('options', queryset=AttributeOption.objects.filter(productattributevalue__product__parent=product).distinct(), to_attr='attr_val')).distinct()]
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

        # check pagination
        dict_values = {'num_queries': 20}
        category = Category.objects.get(name='Category-12')
        category_1 = Category.objects.get(name='Category-1')
        category_2 = Category.objects.get(name='Category-2')
        category_321 = Category.objects.get(name='Category-321')
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 1, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

        # Sorted by price ascending
        dict_values = {'page': 1, 'sorting_type': 'stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        # TODO use price_retail

        # sorting by price descending
        dict_values = {'page': 1, 'sorting_type': '-stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': '-stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': '-stockrecords__price_excl_tax', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

        # sorting by rating
        dict_values = {'page': 1, 'sorting_type': 'rating', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 2, 'sorting_type': 'rating', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)
        dict_values = {'page': 3, 'sorting_type': 'rating', 'num_queries': 20}
        self.assertions_category(category=category, dict_values=dict_values)

        # sorting with filters
        dict_values = {'page': 1, 'sorting_type': 'stockrecords__price_excl_tax', 'num_queries': 20, 'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        self.assertions_category(category=category_321, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'rating', 'num_queries': 20, 'filters': 'shirina_1000/shirina_1200/dlina_1100/dlina_1000'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': '-stockrecords__price_excl_tax', 'num_queries': 20, 'filters': ''}
        self.assertions_category(category=category, dict_values=dict_values)
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        self.assertions_category(category=category_321, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': '-stockrecords__price_excl_tax', 'num_queries': 20, 'filters': 'shirina_1000/shirina_1100/shirina_1200/dlina_1000/dlina_1100'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 2, 'sorting_type': 'rating', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_category(category=category, dict_values=dict_values)

        dict_values = {'page': 1, 'sorting_type': 'rating', 'num_queries': 20, 'filters': 'dlina_1100'}
        self.assertions_category(category=category_1, dict_values=dict_values)
        self.assertions_category(category=category_2, dict_values=dict_values)
        self.assertions_category(category=category_321, dict_values=dict_values)


        # with page not exist
        # current_page = 200
        # response = self.client.get(category.get_absolute_url(), {'page': current_page})
        # products = Product.objects.filter(enable=True, categories__in=category.get_descendants(include_self=True)).distinct()
        # p = Paginator(products, paginate_by)
        # self.assertEqual(list(p.page(1).object_list), list(response.context['page_obj']))

    def assertions_category(self, category, dict_values={}):
        paginate_by = OSCAR_PRODUCTS_PER_PAGE
        only = ['title', 'slug', 'structure', 'product_class', 'product_options__name', 'product_options__code',
                'product_options__type', 'enable', 'categories', 'filters']
        dict_filter = {'enable': True, 'categories__in': category.get_descendants(include_self=True)}

        if dict_values.get('filters'):
            dict_filter['filters__slug__in'] = dict_values.get('filters').split('/')

        products = Product.objects.filter(**dict_filter).only(*only).distinct().select_related('product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('product_options'),
            Prefetch('product_class__options'),
            Prefetch('stockrecords'),
            Prefetch('categories__parent__parent')
        ).distinct().order_by(dict_values.get('sorting_type', *Product._meta.ordering))

        # with self.assertNumQueries(dict_values['num_queries']):
        response = self.client.get(category.get_absolute_url(), dict_values)

        sorting_type = dict_values.get('sorting_type', *Product._meta.ordering)

        products_without_filters = Product.objects.only('id').filter(**dict_filter).distinct().order_by(
            sorting_type)

        queryset_filters = Filter.objects.filter(products__in=products_without_filters).distinct().prefetch_related('products')
        filters = Filter.objects.filter(level=0).prefetch_related(
            Prefetch('children', queryset=queryset_filters, to_attr='children_in_products'),
        ).distinct()

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
        self.assertEqual(list(filters), list(response.context['filters']))

        test_catalogue.test_menu_categories(obj=self, response=response)

        # response = self.client.post(category.get_absolute_url(), dict_values)
        response = self.client.post(category.get_absolute_url(),
                                    json.dumps(dict_values),
                                    content_type='application/json',
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # if response.request['REQUEST_METHOD'] == 'POST':
            # raise Exception('hello')
        context = dict()
        context['products'] = [product.get_values() for product in products]
        self.assertJSONEqual(json.dumps(context), response.content)

