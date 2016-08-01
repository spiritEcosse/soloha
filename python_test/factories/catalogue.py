# -*- coding: utf-8 -*-

import random
from oscar.test import factories
from oscar.core.loading import get_model
from soloha.settings import OSCAR_MISSING_IMAGE_URL
from soloha.settings import MAX_COUNT_PRODUCT, MAX_COUNT_CATEGORIES
from django.test import TestCase
from django.core.management import call_command
from oscar.apps.partner import strategy, availability, prices
from oscar.core.loading import get_class, get_model
from decimal import Decimal as D
from oscar.apps.partner.strategy import Selector
from django.conf import settings
from apps.catalogue.models import SiteInfo
from apps.flatpages.models import InfoPage

Free = get_class('shipping.methods', 'Free')
Info = get_model('sites', 'Info')
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
Partner = get_model('partner', 'Partner')


class Test(object):
    @classmethod
    def create_categories(cls):
        """
        create bulk category
        Returns:
            None
        """
        category_1, created = Category.objects.get_or_create(name='Category-1')
        category_12, created = Category.objects.get_or_create(name='Category-12', parent=category_1)
        category_123, created = Category.objects.get_or_create(name='Category-123', parent=category_12)
        category_1234, created = Category.objects.get_or_create(name='Category-1234', parent=category_123)

        category_2, created = Category.objects.get_or_create(name='Category-2')
        category_3, created = Category.objects.get_or_create(name='Category-3')
        category_31, created = Category.objects.get_or_create(name='Category-31', parent=category_3)
        category_32, created = Category.objects.get_or_create(name='Category-32', parent=category_3)
        category_321, created = Category.objects.get_or_create(name='Category-321', parent=category_32)
        category_33, created = Category.objects.get_or_create(name='Category-33', parent=category_3)
        category_4, created = Category.objects.get_or_create(name='Category-4')
        category_5, created = Category.objects.get_or_create(name='Category-5')
        category_51, created = Category.objects.get_or_create(name='Category-51')
        category_511, created = Category.objects.get_or_create(name='Category-511')
        category_6, created = Category.objects.get_or_create(name='Category-6')
        category_61, created = Category.objects.get_or_create(name='Category-61')
        category_7, created = Category.objects.get_or_create(name='Category-7')
        category_8, created = Category.objects.get_or_create(name='Category-8')
        category_9, created = Category.objects.get_or_create(name='Category-9')
        category_10, created = Category.objects.get_or_create(name='Category-10')

    def create_feature(self):
        feature_1, created = Feature.objects.get_or_create(title='Feature 1')
        feature_11, created = Feature.objects.get_or_create(title='1100', parent=feature_1)
        feature_2, created = Feature.objects.get_or_create(title='Feature 2', bottom_line='60', top_line='3000')
        feature_21, created = Feature.objects.get_or_create(title='2100', parent=feature_2)
        feature_22, created = Feature.objects.get_or_create(title='2200', parent=feature_2)
        feature_23, created = Feature.objects.get_or_create(title='2300', parent=feature_2)
        feature_211, created = Feature.objects.get_or_create(title='Feature 211', parent=feature_21)
        feature_3, created = Feature.objects.get_or_create(title='Feature 3', bottom_line='120', top_line='4000')
        feature_31, created = Feature.objects.get_or_create(title='3100', parent=feature_3)
        feature_32, created = Feature.objects.get_or_create(title='3200', parent=feature_3)
        feature_33, created = Feature.objects.get_or_create(title='3300', parent=feature_3)
        feature_4, created = Feature.objects.get_or_create(title='Feature 4')
        feature_41, created = Feature.objects.get_or_create(title='Feature 41', parent=feature_4)
        feature_5, created = Feature.objects.get_or_create(title='Feature 5')
        feature_51, created = Feature.objects.get_or_create(title='Feature 51', parent=feature_5)
        feature_6, created = Feature.objects.get_or_create(title='Feature 6')
        feature_61, created = Feature.objects.get_or_create(title='Feature 61', parent=feature_6)
        feature_7, created = Feature.objects.get_or_create(title='Feature 7')
        feature_71, created = Feature.objects.get_or_create(title='Feature 71', parent=feature_7)
        feature_8, created = Feature.objects.get_or_create(title='Feature 8')
        feature_81, created = Feature.objects.get_or_create(title='Feature 81', parent=feature_8)
        feature_9, created = Feature.objects.get_or_create(title='Feature 9')
        feature_91, created = Feature.objects.get_or_create(title='Feature 91', parent=feature_9)
        feature_10, created = Feature.objects.get_or_create(title='Feature 10')
        feature_101, created = Feature.objects.get_or_create(title='Feature 101', parent=feature_10)

    # @classmethod
    # def create_stockrecord(cls, product=None, price_excl_tax=None, partner_sku=None,
    #                        num_in_stock=None, partner_name=None,
    #                        currency=OSCAR_DEFAULT_CURRENCY,
    #                        partner_users=None, product_version=None, product_option=None):
    #     if product is None:
    #         product = factories.create_product(title='Product 1000')
    #     partner, __ = Partner.objects.get_or_create(name=partner_name or '')
    #     if partner_users:
    #         for user in partner_users:
    #             partner.users.add(user)
    #     if price_excl_tax is None:
    #         price_excl_tax = D('9.99')
    #     if partner_sku is None:
    #         partner_sku = 'sku_%d_%d' % (product.id, random.randint(0, 10000))
    #
    #     obj = product
    #
    #     if product_version is not None:
    #         obj = product_version
    #     elif product_option is not None:
    #         obj = product_option
    #
    #     return obj.stockrecords.create(
    #         partner=partner, product=product, partner_sku=partner_sku,
    #         price_currency=currency,
    #         price_excl_tax=price_excl_tax, num_in_stock=num_in_stock)

    def create_attributes(self, product):
        self.create_feature()
        feature_1 = Feature.objects.get(title='Feature 1')
        feature_2 = Feature.objects.get(title='Feature 2')
        feature_3 = Feature.objects.get(title='Feature 3')

        feature_11 = Feature.objects.get(title='1100')
        feature_21 = Feature.objects.get(title='2100')
        feature_31 = Feature.objects.get(title='3100')
        feature_32 = Feature.objects.get(title='3200')
        feature_33 = Feature.objects.get(title='3300')

        product_version_1, created = ProductVersion.objects.get_or_create(product=product, price_retail=D('10.10'), cost_price=D('8'))

        ProductFeature.objects.get_or_create(product=product, feature=feature_1, sort=3)
        ProductFeature.objects.get_or_create(product=product, feature=feature_2, sort=1)
        ProductFeature.objects.get_or_create(product=product, feature=feature_3, sort=2)

        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_31)

        product_version_2, created = ProductVersion.objects.get_or_create(product=product, price_retail=D('110.10'), cost_price=D('100'))

        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_32)

        product_version_3, created = ProductVersion.objects.get_or_create(product=product, price_retail=D('1.10'), cost_price=D('1'))

        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_33)

    def create_attribute_option(self, product):
        self.create_feature()
        feature_1 = Feature.objects.get(title='Feature 1')
        feature_2 = Feature.objects.get(title='Feature 2')
        feature_3 = Feature.objects.get(title='Feature 3')

        feature_11 = Feature.objects.get(title='1100')
        feature_21 = Feature.objects.get(title='2100')
        feature_31 = Feature.objects.get(title='3100')
        feature_32 = Feature.objects.get(title='3200')
        feature_33 = Feature.objects.get(title='3300')
        feature_41 = Feature.objects.get(title='Feature 41')
        cost_price = D('10.10')
        product_version_1, created = ProductVersion.objects.get_or_create(product=product, price_retail=cost_price + 100, cost_price=cost_price)

        ProductFeature.objects.get_or_create(product=product, feature=feature_1, sort=3)
        ProductFeature.objects.get_or_create(product=product, feature=feature_2, sort=1)
        ProductFeature.objects.get_or_create(product=product, feature=feature_3, sort=2)

        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_31)

        cost_price = D('110.10')
        product_version_2, created = ProductVersion.objects.get_or_create(product=product, price_retail=cost_price + 100, cost_price=cost_price)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_32)

        cost_price = D('1.10')
        product_version_3, created = ProductVersion.objects.get_or_create(product=product, price_retail=cost_price + 10, cost_price=cost_price)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_33)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_41, price_retail=cost_price + 100, cost_price=cost_price)

    def create_dynamic_attributes(self, product):
        self.create_feature()
        feature_1 = Feature.objects.get(title='Feature 1')
        feature_2 = Feature.objects.get(title='Feature 2')
        feature_3 = Feature.objects.get(title='Feature 3')
        feature_11 = Feature.objects.get(title='1100', parent=feature_1)
        feature_21 = Feature.objects.get(title='2100', parent=feature_2)
        feature_22 = Feature.objects.get(title='2200', parent=feature_2)
        feature_31 = Feature.objects.get(title='3100', parent=feature_3)
        feature_32 = Feature.objects.get(title='3200', parent=feature_3)
        feature_33 = Feature.objects.get(title='3300', parent=feature_3)
        feature_41 = Feature.objects.get(title='Feature 41')

        price_retail = D(2000)
        product_version_1, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_1, attribute=feature_31)

        cost_price = D(2100)
        product_version_2, created = ProductVersion.objects.get_or_create(product=product, price_retail=cost_price + 100, cost_price=cost_price)

        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_32)
        VersionAttribute.objects.get_or_create(version=product_version_2, attribute=feature_41, price_retail=cost_price + D('10.10'), cost_price=cost_price)

        price_retail = D(2200)
        product_version_3, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_21)
        VersionAttribute.objects.get_or_create(version=product_version_3, attribute=feature_33)

        price_retail = D(2300)
        product_version_4, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)
        VersionAttribute.objects.get_or_create(version=product_version_4, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_4, attribute=feature_22)
        VersionAttribute.objects.get_or_create(version=product_version_4, attribute=feature_31)
        price_retail = D(2400)
        product_version_5, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

        VersionAttribute.objects.get_or_create(version=product_version_5, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_5, attribute=feature_22)
        VersionAttribute.objects.get_or_create(version=product_version_5, attribute=feature_32)

        price_retail = D(2600)
        product_version_6, created = ProductVersion.objects.get_or_create(product=product, price_retail=price_retail + 100, cost_price=price_retail)

        VersionAttribute.objects.get_or_create(version=product_version_6, attribute=feature_11)
        VersionAttribute.objects.get_or_create(version=product_version_6, attribute=feature_22)
        VersionAttribute.objects.get_or_create(version=product_version_6, attribute=feature_33)

    def create_options(self, product1, product2):
        self.create_feature()
        option_1 = Feature.objects.get(title='Feature 1')
        option_11 = Feature.objects.get(title='Feature 11')
        option_21 = Feature.objects.get(title='Feature 21')
        option_31 = Feature.objects.get(title='Feature 31')
        option_211 = Feature.objects.get(title='Feature 211')
        option_9 = Feature.objects.get(title='Feature 9')
        ProductOptions.objects.create(product=product1, option=option_11, price_retail=D('1.10'), cost_price=D('1'))
        ProductOptions.objects.create(product=product1, option=option_21, price_retail=D('1.10'), cost_price=D('1'))
        ProductOptions.objects.create(product=product1, option=option_1, price_retail=D('1.10'), cost_price=D('1'))
        ProductOptions.objects.create(product=product1, option=option_211, price_retail=D('1.10'), cost_price=D('1'))
        ProductOptions.objects.create(product=product1, option=option_9, price_retail=D('1.10'), cost_price=D('1'))
        ProductOptions.objects.create(product=product2, option=option_31, price_retail=D('1.10'), cost_price=D('1'))

    def create_product_bulk(self):
        """
        create bulk product with category and object image
        Returns:
            None
        """
        self.create_categories()

        selector = Selector()
        strategy = selector.strategy()

        Feature.objects.get_or_create(title=u'длина', slug='dlina')
        Feature.objects.get_or_create(title=u'ширина', slug='shirina')
        parent_dlina = Feature.objects.get(title=u'длина')
        parent_shirina = Feature.objects.get(title=u'ширина')
        for num in xrange(1000, 1400, 100):
            Feature.objects.get_or_create(title=u'длина_{}'.format(num), slug='dlina_{}'.format(num), parent=parent_dlina)
            Feature.objects.get_or_create(title=u'ширина_{}'.format(num), slug='shirina_{}'.format(num), parent=parent_shirina)

        for num in xrange(1, 10):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            self.create_attributes(product=product)
            factories.create_product_image(product=product, original=OSCAR_MISSING_IMAGE_URL)
            category_123 = Category.objects.get(name='Category-123')
            category_3 = Category.objects.get(name='Category-3')
            category_32 = Category.objects.get(name='Category-32')
            product.categories.add(category_3, category_32, category_123)

            info = strategy.fetch_for_product(product)
            info.availability.num_available = 10

        for num in xrange(10, 40):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            self.create_attributes(product=product)
            category_4 = Category.objects.get(name='Category-4')
            category_3 = Category.objects.get(name='Category-3')
            category_12 = Category.objects.get(name='Category-12')
            category_321 = Category.objects.get(name='Category-321')
            product.categories.add(category_3, category_12, category_321, category_4)

        for num in xrange(40, 50):
            product = factories.create_product(slug='product-{}'.format(num), title='Product {}'.format(num), price=num)
            self.create_attributes(product=product)
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

        call_command('rebuild_index', interactive=False, verbosity=0)

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

    @staticmethod
    def create_site_info():
        SiteInfo.objects.create(domain='example.com', work_time='9:00-19:00', address=('address'),
                                phone_number='0959999999', email='test@gmail.com')

    @staticmethod
    def create_flatpages():
        InfoPage.objects.create(url='delivery', title='Delivery', content='delivery content')
        InfoPage.objects.create(url='payment', title='Payment', content='payment content')
        InfoPage.objects.create(url='manager', title='Mobile manager', content='mobile manager content')
