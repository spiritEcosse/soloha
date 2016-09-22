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
from django.contrib.redirects.models import Redirect


logger = logging.getLogger(__name__)

Product = get_model('catalogue', 'product')
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
        self.stdout.write('Successfully.')

    def create_feature(self, cursor):
        cursor.execute("SELECT product_id, man.name as manufacturer_name from `product`"
                       "INNER JOIN manufacturer man ON(man.manufacturer_id=product.manufacturer_id)")
        products_rows = namedtuplefetchall(cursor)

        for key_product, row_product in enumerate(products_rows):
            left_product = len(products_rows) - key_product + 1
            print '\n\n left product - {} \n\n'.format(left_product)

            cursor.execute("SELECT * from `url_alias` "
                           "WHERE query=CONCAT('product_id=', {})".format(row_product.product_id))

            product_mysql = namedtuplefetchone(cursor)

            if product_mysql is not None:
                print product_mysql.keyword
                try:
                    product = Product.objects.get(slug__iexact=product_mysql.keyword)
                except ObjectDoesNotExist as e:
                    print e
                else:
                    print row_product.manufacturer_name
                    partner = Partner.objects.get(name=row_product.manufacturer_name)
                    product.partner = partner
                    product.save()
