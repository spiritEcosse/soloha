# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.db import connections
from collections import namedtuple
from oscar.core.loading import get_model
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from django.utils.html import escape
from django.utils.html import format_html
from django.utils.safestring import mark_for_escaping
import HTMLParser
from oscar.apps.catalogue.categories import create_from_breadcrumbs
from oscar.core.loading import get_class, get_classes
from decimal import Decimal
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal as D
import random
from django.db import IntegrityError
from django.utils.text import capfirst
import logging
from oscar.core.utils import slugify
from django.utils.text import force_text
from unidecode import unidecode
from collections import OrderedDict
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)

Category = get_model('catalogue', 'category')
Product = get_model('catalogue', 'product')
Feature = get_model('catalogue', 'Feature')
ProductVersion = get_model('catalogue', 'ProductVersion')
ProductFeature = get_model('catalogue', 'ProductFeature')
VersionAttribute = get_model('catalogue', 'VersionAttribute')
ProductClass = get_model('catalogue', 'ProductClass')
ProductCategory = get_model('catalogue', 'ProductCategory')
Partner, StockRecord = get_classes('partner.models', ['Partner', 'StockRecord'])


def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def namedtuplefetchone(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    data = cursor.fetchone()

    if data is not None:
        return nt_result(*data)


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Migrate data from mysql db soloha in posgresql
        :param args:
        :param options:
        :return:
        """
        cursor = connections['mysql'].cursor()

        self.create_feature(cursor)
        self.stdout.write('Successfully migrate date from db mysql soloha')

    def create_feature(self, cursor):
        # cursor.execute("SELECT product_id from `product` WHERE product_id={}".format(68))
        cursor.execute("SELECT product_id, price, product.manufacturer_id as product_manufacturer_id from `product` "
                       "INNER JOIN manufacturer man ON(man.manufacturer_id=product.manufacturer_id) "
                       "Where product.product_id=57076 LIMIT 10")

        products_rows = namedtuplefetchall(cursor)
        len_products = len(products_rows)

        for key_product, row_product in enumerate(products_rows):
            left_product = len_products - key_product + 1
            print '\n\n left product - {} \n\n'.format(left_product)

            product = self.get_product(cursor, row_product.product_id)
            print row_product.price

            # product.partner =
            # partner_name = row_product.manufacturer_name
            # partner_sku = ''
            #
            # partner, _ = Partner.objects.get_or_create(name=partner_name)
            # try:
            #     stock = StockRecord.objects.get(partner_sku=partner_sku)
            # except StockRecord.DoesNotExist:
            #     stock = StockRecord()
            #
            # stock.product = product
            # stock.partner = partner
            # stock.partner_sku = partner_sku
            # stock.price_excl_tax = Decimal(row_product.price)
            # stock.num_in_stock = 0
            # stock.save()

    def get_product(self, cursor, product_id):
        cursor.execute("SELECT * from `url_alias` "
                       "WHERE query=CONCAT('product_id=', {})".format(product_id))

        product_mysql = namedtuplefetchone(cursor)

        if product_mysql is not None:
            try:
                product = Product.objects.get(slug=product_mysql.keyword)
                print product.slug, product_id
            except Product.DoesNotExist:
                logger.error(u'Product with slug - {} DoesNotExist'.format(product_mysql.keyword))
