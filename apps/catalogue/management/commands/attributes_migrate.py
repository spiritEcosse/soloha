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
        cursor.execute("SELECT product_id from `product`")
        products_rows = namedtuplefetchall(cursor)
        new_dict_feature = {'option': {}, 'value': {}}
        auto_created = {}

        for key_product, row_product in enumerate(products_rows):
            print 'left product - {}'.format(len(products_rows) - key_product + 1)

            cursor.execute("SELECT * from `url_alias` "
                           "WHERE query=CONCAT('product_id=', {})".format(row_product.product_id))

            product_mysql = namedtuplefetchone(cursor)

            if product_mysql is not None:
                try:
                    product = Product.objects.get(slug=product_mysql.keyword)
                    print product.slug, row_product.product_id
                except Product.DoesNotExist:
                    logger.error(u'Product with slug - {} DoesNotExist'.format(product_mysql.keyword))
                else:
                    product.versions.all().delete()
                    product.product_features.all().delete()
                    VersionAttribute.objects.filter(version__product=product).delete()

                    cursor.execute("SELECT * from `product_table` "
                                   "WHERE product_id={} and type_table=0".format(row_product.product_id))
                    rows_tables = namedtuplefetchall(cursor)

                    for row_product_table in rows_tables:
                        cursor.execute("SELECT * from product_table_option where vertical = 0 AND product_table_id={}".
                                       format(row_product_table.product_table_id))

                        if namedtuplefetchall(cursor):
                            cursor.execute("SELECT * from product_table_option where option_id = 48 And product_table_id={}".
                                           format(row_product_table.product_table_id))

                            if not namedtuplefetchall(cursor):
                                cursor.execute("SELECT ptovp.price, od.name as name_option, ovd.name as name_value,  "
                                               "od_1.name as name_option_1, ovd_1.name as name_value_1, ovd_1.option_value_id as option_1_value_id, "
                                               "od.option_id, ovd.option_value_id "
                                               "from `product_table_option_value_price` ptovp "
                                               "LEFT JOIN `option_value_description` as ovd ON (ptovp.option_value_horizont=ovd.option_value_id) "
                                               "LEFT JOIN `option_description` as od ON (od.option_id=ovd.option_id) "
                                               "LEFT JOIN `option_value_description` as ovd_1 ON (ptovp.option_value_vertical=ovd_1.option_value_id) "
                                               "LEFT JOIN `option_description` as od_1 ON (od_1.option_id=ovd_1.option_id) "
                                               "WHERE ptovp.product_table_id={} AND ptovp.price != 0.0000".
                                               format(row_product_table.product_table_id))

                                options = namedtuplefetchall(cursor)
                                data_values, count_option_value = self.get_values(cursor, options, row_product_table.product_table_id)
                                key_value = 0

                                for key, option in enumerate(options):
                                    print row_product.product_id, option.option_id, option.option_value_id, option.price

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
                                                product_for_feature = Product.objects.get(slug=product_mysql_fabric.keyword)
                                            except Product.DoesNotExist:
                                                logger.error(u'Product with slug (product_with_images) - {} DoesNotExist'.
                                                             format(product_mysql_fabric.keyword))
                                            else:
                                                products.append(product_for_feature)

                                    version = ProductVersion.objects.create(product=product, price_retail=option.price, cost_price=option.price)

                                    if option.name_option_1 is not None and option.name_value_1 is not None:
                                        feature = self.get_feature(option=option.name_option_1, value=option.name_value_1, new_dict_feature=new_dict_feature, auto_created=auto_created)
                                        VersionAttribute.objects.create(version=version, attribute=feature)

                                    feature = self.get_feature(option=option.name_option, value=option.name_value, new_dict_feature=new_dict_feature, auto_created=auto_created)
                                    VersionAttribute.objects.create(version=version, attribute=feature)

                                    if products:
                                        try:
                                            ProductFeature.objects.get(product=product, feature=feature)
                                        except ProductFeature.DoesNotExist:
                                            product_feature = ProductFeature.objects.create(product=product,
                                                                                            feature=feature)
                                            product_feature.product_with_images.add(*products)

                                    for value in data_values.values():
                                        try:
                                            temp_value = value[key_value]
                                        except IndexError:
                                            pass
                                        else:
                                            feature = self.get_feature(option=temp_value.name, value=temp_value.ovd_name, new_dict_feature=new_dict_feature, auto_created=auto_created)
                                            VersionAttribute.objects.create(version=version, attribute=feature)

                                    key_value += 1

                                    if key_value == count_option_value:
                                        key_value = 0

    def get_feature(self, option, value, new_dict_feature, auto_created):
        try:
            feature = Feature.objects.get(title=option)
        except Feature.DoesNotExist:
            slugify_option = slugify(option)

            if slugify_option not in new_dict_feature['option']:
                create = ''

                while create != '1' and create != '0':
                    create = raw_input('Create this feature "{}" ? (1/0)'.format(slugify_option))

                if int(create):
                    feature = Feature.objects.create(title=option)
                else:
                    feature = Feature.objects.get(slug=raw_input('Enter valid slug: '))

                new_dict_feature['option'][slugify_option] = feature
            else:
                feature = Feature.objects.get(slug=new_dict_feature['option'][slugify_option])
        else:
            slugify_option = feature.slug

        try:
            feature_value = Feature.objects.get(title=value, parent=feature)
        except Feature.DoesNotExist:
            slugify_value = u'{}-{}'.format(feature.slug, slugify(value))

            if slugify_option in auto_created:
                feature_value = Feature.objects.create(title=value, parent=feature)
            elif slugify_value not in new_dict_feature['value']:
                create = ''

                while create != '1' and create != '0':
                    create = raw_input('Create this feature "{}" of parent - {}? (1/0)'.format(slugify_value, slugify_option))

                if int(create):
                    feature_value = Feature.objects.create(title=value, parent=feature)
                else:
                    feature_value = Feature.objects.get(slug=raw_input('Enter valid slug: '))

                new_dict_feature['value'][slugify_value] = feature_value.slug

                create_auto = ''

                while create_auto != '1' and create_auto != '0':
                    create_auto = raw_input('Auto create children for this feature in future "{}" ? (1/0)'.format(slugify_option))

                if int(create_auto):
                    auto_created[slugify_option] = True
            else:
                feature_value = Feature.objects.get(slug=new_dict_feature['value'][slugify_value])

        return feature_value

    def get_values(self, cursor, options, product_table_id):
        list_option_1_value = list(set([option.option_1_value_id for option in options]))
        list_option_value = list(set([option.option_value_id for option in options]))
        list_full_value = list_option_1_value + list_option_value

        cursor.execute("SELECT od.name, pto.product_table_id, pto.vertical, ovd.name as ovd_name, "
                       "ptov.option_value_id, ptov.product_table_option_value_sort as sort, ovd.option_id "
                       "from `product_table_option` as pto "
                       "NATURAL JOIN `option_description` as od "
                       "NATURAL JOIN `product_table_option_value` as ptov "
                       "INNER JOIN `option_value_description` as ovd ON (ptov.option_value_id=ovd.option_value_id) "
                       "WHERE pto.product_table_id={} AND vertical = 1 AND ovd.name != '---' "
                       "ORDER BY sort, ptov.product_table_option_value_id".format(product_table_id))

        data_values = {}

        for value in namedtuplefetchall(cursor):
            if value.option_value_id not in list_full_value:
                if value.option_id in data_values:
                    data_values[value.option_id].append(value)
                else:
                    data_values[value.option_id] = [value]

        return data_values, len(list_option_1_value)
