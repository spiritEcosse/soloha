# -*- coding: utf-8 -*-

from oscar.test import factories
from oscar.core.loading import get_model
from soloha.settings import OSCAR_MISSING_IMAGE_URL
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from django.test import TestCase
from apps.catalogue.models import Filter

ProductCategory = get_model('catalogue', 'productcategory')
Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class Test(object):
    @classmethod
    def create_categories(cls):
        """
        create bulk category
        Returns:
            None
        """
        category_1 = Category.objects.create(name='Category-1')
        category_12 = Category.objects.create(name='Category-12', parent=category_1)
        category_123 = Category.objects.create(name='Category-123', parent=category_12)
        category_1234 = Category.objects.create(name='Category-1234', parent=category_123)

        category_2 = Category.objects.create(name='Category-2')
        category_3 = Category.objects.create(name='Category-3')
        category_31 = Category.objects.create(name='Category-31', parent=category_3)
        category_32 = Category.objects.create(name='Category-32', parent=category_3)
        category_321 = Category.objects.create(name='Category-321', parent=category_32)
        category_33 = Category.objects.create(name='Category-33', parent=category_3)
        category_4 = Category.objects.create(name='Category-4')
        category_5 = Category.objects.create(name='Category-5')
        category_51 = Category.objects.create(name='Category-51')
        category_511 = Category.objects.create(name='Category-511')
        category_6 = Category.objects.create(name='Category-6')
        category_61 = Category.objects.create(name='Category-61')
        category_7 = Category.objects.create(name='Category-7')
        category_8 = Category.objects.create(name='Category-8')
        category_9 = Category.objects.create(name='Category-9')
        category_10 = Category.objects.create(name='Category-10')

    def create_product_bulk(self):
        """
        create bulk product with category and object image
        Returns:
            None
        """
        self.create_categories()

        Filter.objects.create(title=u'длина', slug='dlina')
        Filter.objects.create(title=u'ширина', slug='shirina')
        parent_dlina = Filter.objects.get(title=u'длина')
        parent_shirina = Filter.objects.get(title=u'ширина')
        for num in xrange(1000, 1400, 100):
            Filter.objects.create(title=u'длина_{}'.format(num), slug='dlina_{}'.format(num), parent=parent_dlina)
            Filter.objects.create(title=u'ширина_{}'.format(num), slug='shirina_{}'.format(num), parent=parent_shirina)

        for num in xrange(1, 11):
            product = factories.create_product(title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product, original=OSCAR_MISSING_IMAGE_URL)
            category_123 = Category.objects.get(name='Category-123')
            category_3 = Category.objects.get(name='Category-3')
            category_32 = Category.objects.get(name='Category-32')
            product.categories.add(category_3, category_32, category_123)

        for num in xrange(10, 41):
            product = factories.create_product(title='Product {}'.format(num), price=num)
            category_4 = Category.objects.get(name='Category-4')
            category_3 = Category.objects.get(name='Category-3')
            category_12 = Category.objects.get(name='Category-12')
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_3, category_12, category_321, category_4)

        for num in xrange(40, 51):
            product = factories.create_product(title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product, original=OSCAR_MISSING_IMAGE_URL)
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_321)

        for num in xrange(50, 61):
            product = factories.create_product(title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product)

        for num in xrange(60, 119):
            product = factories.create_product(title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product)
            category_12 = Category.objects.get(name='Category-12')
            product.categories.add(category_12)
            if num < 70:
                product.filters.add(Filter.objects.get(title=u'длина_1000'))
                product.filters.add(Filter.objects.get(title=u'ширина_1000'))
            elif num < 80:
                product.filters.add(Filter.objects.get(title=u'длина_1000'))
                product.filters.add(Filter.objects.get(title=u'ширина_1100'))
            elif num < 90:
                product.filters.add(Filter.objects.get(title=u'длина_1100'))
                product.filters.add(Filter.objects.get(title=u'ширина_1000'))
            elif num < 100:
                product.filters.add(Filter.objects.get(title=u'длина_1200'))
                product.filters.add(Filter.objects.get(title=u'ширина_1100'))
            else:
                product.filters.add(Filter.objects.get(title=u'длина_1100'))
                product.filters.add(Filter.objects.get(title=u'ширина_1200'))

    def create_product_bulk_recommend(self):
        """
        create product bulk with model ProductRecommendation
        Returns:
            None
        """
        self.create_product_bulk()
        product_desc = Product.objects.all().order_by('-date_created')
        product_asc = Product.objects.all().order_by('date_created')

        for num in xrange(0, len(product_desc)):
            ProductRecommendation.objects.create(primary=product_desc[num], recommendation=product_asc[num])

    def test_menu_categories(self, obj, response):
        categories_expected = Category.objects.filter(enable=True, level=0).select_related(
            'parent__parent'
        ).prefetch_related('children__children')[:MAX_COUNT_CATEGORIES]
        obj.assertEqual(str(categories_expected.query), str(response.context['categories'].query))
        categories_expected = [category.get_values() for category in categories_expected]
        with obj.assertNumQueries(0):
            categories = [category.get_values() for category in response.context['categories']]
        obj.assertListEqual(list(categories_expected), list(categories))

    @classmethod
    def create_order(cls):
        for num in xrange(1, 20):
            factories.create_order()
