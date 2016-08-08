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
import texttable
from django.utils.text import force_text
from unidecode import unidecode
from collections import OrderedDict
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
        cursor.execute("SELECT * from `product` WHERE product_id={}".format(55529))

        for row_product in namedtuplefetchall(cursor):
            cursor.execute("SELECT * from `url_alias` "
                           "WHERE query=CONCAT('product_id=', {})".format(row_product.product_id))

            product_mysql = namedtuplefetchone(cursor)

            if product_mysql is not None:
                try:
                    product = Product.objects.get(slug=product_mysql.keyword)
                except Product.DoesNotExist:
                    logger.error(u'Product with slug - {} DoesNotExist'.format(product_mysql.keyword))
                else:
                    product.versions.all().delete()
                    product.product_features.all().delete()
                    cursor.execute("SELECT * from `product_table` "
                                   "WHERE product_id={} and type_table=0".format(row_product.product_id))
                    rows_tables = namedtuplefetchall(cursor)

                    for row_product_table in rows_tables:
                        cursor.execute("SELECT ptovp.price, od.name as name_option, ovd.name as name_value,  "
                                       "od_1.name as name_option_1, ovd_1.name as name_value_1, ovd_1.option_value_id as option_1_value_id, "
                                       "od.option_id, ovd.option_value_id "
                                       "from `product_table_option_value_price` ptovp "
                                       "LEFT JOIN `option_value_description` as ovd ON (ptovp.option_value_horizont=ovd.option_value_id) "
                                       "LEFT JOIN `option_description` as od ON (od.option_id=ovd.option_id) "
                                       "LEFT JOIN `option_value_description` as ovd_1 ON (ptovp.option_value_vertical=ovd_1.option_value_id) "
                                       "LEFT JOIN `option_description` as od_1 ON (od_1.option_id=ovd_1.option_id) "
                                       "WHERE ptovp.product_table_id={} AND ptovp.price != 0.0000".format(row_product_table.product_table_id))

                        table = texttable.Texttable()
                        table.set_deco(texttable.Texttable.HEADER)
                        table.set_cols_dtype(['f', 't', 't', 't', 't'])
                        table.set_cols_align(["r", "r", "r", "r", "r"])
                        data_table = [
                            ['price', 'option_name', 'option_value_name', 'option_name_1', 'option_value_name_1']]
                        options = namedtuplefetchall(cursor)

                        for row_option in options:
                            data_table.append(
                                [row_option.price, slugify(row_option.name_value), slugify(row_option.name_option),
                                 slugify(row_option.name_value_1), slugify(row_option.name_option_1)])
                        table.add_rows(data_table)

                        print table.draw()
                        print '\n'
                        migrate = int(raw_input('Migrate this table ? (1/0)'))

                        if migrate:
                            list_option_1_value = list(set([option.option_1_value_id for option in options]))
                            list_option_value = list(set([option.option_value_id for option in options]))
                            list_full_value = list_option_1_value + list_option_value

                            for key, option in enumerate(options):
                                cursor.execute("SELECT t3.product_id "
                                               "FROM product_fabric_option as t1 "
                                               "NATURAL JOIN product_fabric_option_value as t2 "
                                               "JOIN product_fabric_option_value_product as t3 "
                                               "NATURAL JOIN product_description AS t4 "
                                               "NATURAL JOIN product AS t5 ON (t2.product_fabric_option_value_id = t3.product_fabric_option_value_id) "
                                               "JOIN manufacturer AS t6 ON(t5.manufacturer_id=t6.manufacturer_id) "
                                               "WHERE t1.product_id = {} AND t1.option_id = {} AND t2.option_value_id = {}".format(
                                    row_product.product_id, option.option_id, option.option_value_id
                                ))

                                products = []

                                for row_product_fabric in namedtuplefetchall(cursor):
                                    cursor.execute("SELECT * from `url_alias` "
                                                   "WHERE query=CONCAT('product_id=', {})".format(row_product_fabric.product_id))

                                    product_mysql_fabric = namedtuplefetchone(cursor)

                                    if product_mysql_fabric is not None:
                                        try:
                                            product = Product.objects.get(slug=product_mysql_fabric.keyword)
                                        except Product.DoesNotExist:
                                            logger.error(u'Product with slug (product_with_images) - {} DoesNotExist'.
                                                         format(product_mysql_fabric.keyword))
                                        else:
                                            products.append(product)

                                # defer_attribute.append()
                                version = ProductVersion.objects.create(product=product, price_retail=option.price, cost_price=option.price)
                                feature = self.get_feature(option=option.name_option_1, value=option.name_value_1)
                                VersionAttribute.objects.create(version=version, attribute=feature)
                                feature = self.get_feature(option=option.name_option, value=option.name_value)
                                VersionAttribute.objects.create(version=version, attribute=feature)

                                if products:
                                    try:
                                        ProductFeature.objects.get(product=product, feature=feature)
                                    except ProductFeature.DoesNotExist:
                                        product_feature = ProductFeature.objects.create(product=product, feature=feature)
                                        product_feature.product_with_images.add(*products)

                                cursor.execute("SELECT od.name, pto.product_table_id, pto.vertical, ovd.name as ovd_name, "
                                               "ptov.option_value_id, ptov.product_table_option_value_sort as sort, ovd.option_id "
                                               "from `product_table_option` as pto "
                                               "NATURAL JOIN `option_description` as od "
                                               "NATURAL JOIN `product_table_option_value` as ptov "
                                               "INNER JOIN `option_value_description` as ovd ON (ptov.option_value_id=ovd.option_value_id) "
                                               "WHERE pto.product_table_id={} AND vertical = 1 AND ovd.option_id NOT IN ({}) "
                                               "ORDER BY sort, ptov.product_table_option_value_id".format(
                                    row_product_table.product_table_id, option.option_id))

                                data_values = {}

                                for value in namedtuplefetchall(cursor):
                                    if value.option_value_id not in list_full_value:
                                        if value.option_id in data_values:
                                            data_values[value.option_id].append(value)
                                        else:
                                            data_values[value.option_id] = [value]

                                for value in data_values.values():
                                    try:
                                        temp_value = value[key]
                                    except IndexError:
                                        logger.error('Error list - {} has not index {}'.format(value, key))
                                    else:
                                        feature = self.get_feature(option=temp_value.name, value=temp_value.ovd_name)
                                        VersionAttribute.objects.create(version=version, attribute=feature)

                        print '\n\n'

    def get_feature(self, option, value):
        try:
            feature = Feature.objects.get(title=option)
        except Feature.DoesNotExist:
            create = int(raw_input('Create this feature "{}" ? (1/0)'.format(slugify(option))))

            if create:
                feature = Feature.objects.create(title=option)
            else:
                feature = Feature.objects.get(slug=raw_input('Enter valid slug: '))

        try:
            feature_value = Feature.objects.get(title=value, parent=feature)
        except Feature.DoesNotExist:
            create = int(raw_input('Create this feature "{}" ? (1/0)'.format(slugify(value))))

            if create:
                feature_value = Feature.objects.create(title=value, parent=feature)
            else:
                feature_value = Feature.objects.get(slug=raw_input('Enter valid slug: '))

        return feature_value
