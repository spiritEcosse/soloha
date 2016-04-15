# -*- coding: utf-8 -*-

from oscar.test import factories
from oscar.core.loading import get_model
from soloha.settings import OSCAR_MISSING_IMAGE_URL
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from django.test import TestCase
from oscar.apps.partner import strategy, availability, prices
from oscar.core.loading import get_class, get_model
from decimal import Decimal as D

Free = get_class('shipping.methods', 'Free')
ProductCategory = get_model('catalogue', 'ProductCategory')
Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
ProductFeature = get_model('catalogue', 'ProductFeature')
ProductVersion = get_model('catalogue', 'ProductVersion')
Feature = get_model('catalogue', 'Feature')
VersionAttribute = get_model('catalogue', 'VersionAttribute')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
Basket = get_model('basket', 'Basket')
OrderCreator = get_class('order.utils', 'OrderCreator')
OrderTotalCalculator = get_class('checkout.calculators', 'OrderTotalCalculator')
ProductOptions = get_model('catalogue', 'ProductOptions')


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

    def create_feature(self):
        feature_1 = Feature.objects.create(title='Feature 1')
        feature_11 = Feature.objects.create(title='Feature 11', parent=feature_1)
        feature_2 = Feature.objects.create(title='Feature 2')
        feature_21 = Feature.objects.create(title='Feature 21', parent=feature_2)
        feature_211 = Feature.objects.create(title='Feature 211', parent=feature_21)
        feature_3 = Feature.objects.create(title='Feature 3')
        feature_31 = Feature.objects.create(title='Feature 31', parent=feature_3)
        feature_4 = Feature.objects.create(title='Feature 4')
        feature_41 = Feature.objects.create(title='Feature 41', parent=feature_4)
        feature_5 = Feature.objects.create(title='Feature 5')
        feature_51 = Feature.objects.create(title='Feature 51', parent=feature_5)
        feature_6 = Feature.objects.create(title='Feature 6')
        feature_61 = Feature.objects.create(title='Feature 61', parent=feature_6)
        feature_7 = Feature.objects.create(title='Feature 7')
        feature_71 = Feature.objects.create(title='Feature 71', parent=feature_7)
        feature_8 = Feature.objects.create(title='Feature 8')
        feature_81 = Feature.objects.create(title='Feature 81', parent=feature_8)
        feature_9 = Feature.objects.create(title='Feature 9')
        feature_91 = Feature.objects.create(title='Feature 91', parent=feature_9)
        feature_10 = Feature.objects.create(title='Feature 10')
        feature_101 = Feature.objects.create(title='Feature 101', parent=feature_10)

    def create_attributes(self, product):
        self.create_feature()
        feature_11 = Feature.objects.get(title='Feature 11')
        feature_21 = Feature.objects.get(title='Feature 21')
        feature_31 = Feature.objects.get(title='Feature 31')
        product_version_1 = ProductVersion.objects.create(product=product)
        VersionAttribute.objects.create(version=product_version_1, attribute=feature_11)
        VersionAttribute.objects.create(version=product_version_1, attribute=feature_21)
        VersionAttribute.objects.create(version=product_version_1, attribute=feature_31)
        product_version_2 = ProductVersion.objects.create(product=product)
        VersionAttribute.objects.create(version=product_version_2, attribute=feature_11)

    def create_options(self, product1, product2):
        self.create_feature()
        option_1 = Feature.objects.get(title='Feature 1')
        option_11 = Feature.objects.get(title='Feature 11')
        option_21 = Feature.objects.get(title='Feature 21')
        option_31 = Feature.objects.get(title='Feature 31')
        option_211 = Feature.objects.get(title='Feature 211')
        ProductOptions.objects.create(product=product1, option=option_11)
        ProductOptions.objects.create(product=product1, option=option_21)
        ProductOptions.objects.create(product=product1, option=option_1)
        ProductOptions.objects.create(product=product1, option=option_211)
        ProductOptions.objects.create(product=product2, option=option_31)

    def create_product_bulk(self):
        """
        create bulk product with category and object image
        Returns:
            None
        """
        self.create_categories()

        Feature.objects.create(title=u'длина', slug='dlina')
        Feature.objects.create(title=u'ширина', slug='shirina')
        parent_dlina = Feature.objects.get(title=u'длина')
        parent_shirina = Feature.objects.get(title=u'ширина')
        for num in xrange(1000, 1400, 100):
            Feature.objects.create(title=u'длина_{}'.format(num), slug='dlina_{}'.format(num), parent=parent_dlina)
            Feature.objects.create(title=u'ширина_{}'.format(num), slug='shirina_{}'.format(num), parent=parent_shirina)

        for num in xrange(1, 10):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product, original=OSCAR_MISSING_IMAGE_URL)
            category_123 = Category.objects.get(name='Category-123')
            category_3 = Category.objects.get(name='Category-3')
            category_32 = Category.objects.get(name='Category-32')
            product.categories.add(category_3, category_32, category_123)

        for num in xrange(10, 40):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            category_4 = Category.objects.get(name='Category-4')
            category_3 = Category.objects.get(name='Category-3')
            category_12 = Category.objects.get(name='Category-12')
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_3, category_12, category_321, category_4)

        for num in xrange(40, 50):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product, original=OSCAR_MISSING_IMAGE_URL)
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_321)

        for num in xrange(50, 60):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product)

        for num in xrange(60, 119):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            factories.create_product_image(product=product)
            category_12 = Category.objects.get(name='Category-12')
            category_3 = Category.objects.get(name='Category-3')
            category_321 = Category.objects.get(name='Category-321')
            if num < 70:
                product.categories.add(category_12)
                product.filters.add(Feature.objects.get(title=u'длина_1000'))
                product.filters.add(Feature.objects.get(title=u'ширина_1000'))
            elif num < 80:
                product.categories.add(category_3)
                product.filters.add(Feature.objects.get(title=u'длина_1000'))
                product.filters.add(Feature.objects.get(title=u'ширина_1100'))
            elif num < 90:
                product.categories.add(category_321)
                product.filters.add(Feature.objects.get(title=u'длина_1100'))
                product.filters.add(Feature.objects.get(title=u'ширина_1000'))
            elif num < 100:
                product.categories.add(category_12)
                product.filters.add(Feature.objects.get(title=u'длина_1200'))
                product.filters.add(Feature.objects.get(title=u'ширина_1100'))
            else:
                product.categories.add(category_12)
                product.filters.add(Feature.objects.get(title=u'длина_1100'))
                product.filters.add(Feature.objects.get(title=u'ширина_1200'))

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

    def create_order(self):
        for num in xrange(200, 220):
            self.factory_create_order(num=num)

    @classmethod
    def factory_create_order(cls, number=None, basket=None, user=None, shipping_address=None,
                             shipping_method=None, billing_address=None,
                             total=None, num=0, **kwargs):
        """
        Helper method for creating an order for testing
        """
        if not basket:
            basket = Basket.objects.create()
            basket.strategy = strategy.Default()
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num))
            factories.create_stockrecord(
                product, num_in_stock=10, price_excl_tax=D('10.00'))
            basket.add_product(product)
        if not basket.id:
            basket.save()
        if shipping_method is None:
            shipping_method = Free()
        shipping_charge = shipping_method.calculate(basket)
        if total is None:
            total = OrderTotalCalculator().calculate(basket, shipping_charge)
        order = OrderCreator().place_order(
            order_number=number,
            user=user,
            basket=basket,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            shipping_charge=shipping_charge,
            billing_address=billing_address,
            total=total,
            **kwargs)
        basket.set_as_submitted()
        return order