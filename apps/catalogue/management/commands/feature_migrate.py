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
    return nt_result(*cursor.fetchone())


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Migrate data from mysql db soloha in posgresql
        :param args:
        :param options:
        :return:
        """
        cursor = connections['mysql'].cursor()
        data_option = ('Производитель', 'Плотность(г/м кв.)', 'Состав', 'ШКАФЫ-КУПЕ ПО ТИПУ', 'Категории мебельной ткани',
                       'МАТРАСЫ ПО ТИПУ', 'Тест Мартиндейла', 'Ширина матраса, мм', 'Тип рисунка', 'Уровень жесткости',
                       'Стиль', 'Ширина подушки, мм', 'Зима / лето', 'Антикоготь', 'Максимальная нагрузка, кг',
                       'Высота, мм', 'Длина, мм', 'Особенность')

        def create_feature():
            for option in data_option:
                cursor.execute("SELECT * from `category_option_description` as cod where cod.name='{}'".format(option))

                for row in namedtuplefetchall(cursor):
                    slug = slugify(row.name)
                    feature, create = Feature.objects.get_or_create(slug=slug)

                    if not feature.title:
                        feature.title = row.name
                        feature.save()
                    print feature, create

                    cursor.execute("SELECT * from `category_option_value_description` as covd where covd.option_id={}".format(row.option_id))

                    for row_value in namedtuplefetchall(cursor):
                        slug_value = slug + '-' + slugify(row_value.name)
                        feature_value, create = Feature.objects.get_or_create(slug=slug_value, parent=feature)

                        if not feature_value.title:
                            feature_value.title = row_value.name
                            feature_value.save()

                        print feature_value, create
                        cursor.execute("SELECT * from `product_to_value` as ptv where ptv.value_id={}".format(row_value.value_id))

                        for row_product_value in namedtuplefetchall(cursor):
                            cursor.execute("SELECT * from `url_alias` WHERE query=CONCAT('product_id=', {})".format(row_product_value.product_id))

                            for row_product in namedtuplefetchall(cursor):
                                try:
                                    product = Product.objects.get(slug=row_product.keyword)
                                except Product.DoesNotExist:
                                    logger.error(u'Product with slug - {} DoesNotExist'.format(row_product.keyword))
                                else:
                                    print product
                                    product.filters.add(feature_value)

        create_feature()
        self.stdout.write('Successfully migrate date from db mysql soloha')