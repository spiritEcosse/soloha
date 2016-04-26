# --coding: utf-8--

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
        html_parser = HTMLParser.HTMLParser()
        ProductFeature.objects.all().delete()
        ProductVersion.objects.all().delete()
        Product.objects.all().delete()
        Feature.objects.all().delete()
        Category.objects.all().delete()
        product_class = ProductClass.objects.create(name=u'Общий', requires_shipping=False, track_stock=False)

        def save_product():
            cursor.execute("SELECT product.manufacturer_id as product_manufacturer_id, product_description.name as name,"
                           "product_description.description as description, product_description.meta_keyword as meta_keyword,"
                           "product_description.seo_h1 as seo_h1, product_description.seo_title as seo_title,"
                           "product_description.meta_description as meta_description,"
                           "product.status as status, man.name as manufacturer_name, product.image as image,"
                           "product.price as price, product.product_id as product_id, url.keyword as keyword,"
                           "product_to_category.category_id as category_id "
                           "FROM product "
                           "NATURAL JOIN product_description NATURAL JOIN product_to_category "
                           "Inner JOIN url_alias as url ON (CONCAT('product_id=', product.product_id)=query) "
                           "INNER JOIN manufacturer man ON(man.manufacturer_id=product.manufacturer_id)"
                           "WHERE main_category={} ORDER BY product.product_id".format(1))

            for row in namedtuplefetchall(cursor):
                params = {'title': row.name,
                          'description': html_parser.unescape(row.description),# sdsdsd
                          'slug': row.keyword, #ToDo igor: make safety
                          'enable': bool(row.status), 'meta_title': row.seo_title,
                          'meta_description': row.meta_description, 'meta_keywords': row.meta_keyword, 'h1': row.seo_h1,
                          'product_class': product_class}
                product = Product(**params)
                try:
                    product.save()
                except IntegrityError:
                    print u'Dublicate product - {}'.format(product.title)
                else:
                    cursor.execute("SELECT * FROM url_alias WHERE query=CONCAT('category_id=', {})".format(row.category_id))
                    res = cursor.fetchone()

                    if res:
                        slug = res[2]

                        try:
                            category = Category.objects.get(slug=slug)
                        except ObjectDoesNotExist:
                            pass
                        else:
                            product.categories.add(category)

                    product.images.create(original=row.image)
                    partner_name = row.manufacturer_name
                    partner_sku = ''

                    partner, _ = Partner.objects.get_or_create(name=partner_name)
                    try:
                        stock = StockRecord.objects.get(partner_sku=partner_sku)
                    except StockRecord.DoesNotExist:
                        stock = StockRecord()

                    stock.product = product
                    stock.partner = partner
                    stock.partner_sku = partner_sku
                    stock.price_excl_tax = Decimal(row.price)
                    stock.num_in_stock = 0
                    stock.save()

                    cursor.execute("SELECT * FROM product_image WHERE product_id={}".format(row.product_id))

                    for display_order, image in enumerate(namedtuplefetchall(cursor), start=1):
                        product.images.create(original=image.image, display_order=display_order)

                    product.save()

        def save_category(parent_cat=None, parent_cat_id=0):
            cursor.execute("SELECT * FROM category as cat NATURAL JOIN category_description Inner JOIN url_alias "
                           "as url ON (CONCAT('category_id=', cat.category_id)=query) "
                           "WHERE parent_id={} AND cat.status={}".format(parent_cat_id, 1))

            for row in namedtuplefetchall(cursor):
                dict_param = {'name': row.name, 'description': html_parser.unescape(row.description), 'image': row.image,
                              'slug': row.keyword, 'enable': bool(row.status), 'meta_title': row.seo_title,
                              'meta_description': row.meta_description, 'meta_keywords': row.meta_keyword,
                              'h1': row.seo_h1, 'sort': row.sort_order}
                category = Category.objects.create(**dict_param)

                if parent_cat is not None:
                    parent_cat.children.add(category)

                save_category(category, row.category_id)

        def create_feature_val(feature):
            for num in xrange(1000, 2000, 10):
                Feature.objects.get_or_create(slug='{}-{}'.format(feature.slug, num), title=num, parent=feature)

        def create_feature():
            feature_width, created = Feature.objects.get_or_create(title=u'Ширина, мм')
            create_feature_val(feature_width)
            feature_length, created = Feature.objects.get_or_create(title=u'Длина, мм')
            create_feature_val(feature_length)
            feature_height, created = Feature.objects.get_or_create(title=u'Высота, мм')
            create_feature_val(feature_height)

            for product in Product.objects.all().order_by('?')[:1000]:
                product.filters.add(*Feature.objects.filter(level=1).order_by('?')[:10])

                # for num in xrange(3):
                #     attribute_width = VersionAttribute(attribute=feature_width.children.all()[num])
                #
                #     for num in xrange(3):
                #         attribute_length = VersionAttribute(attribute=feature_length.children.all()[num])
                #
                #         for num in xrange(3):
                #             price_retail = D(random.randint(1, 10000))
                #             version = product.versions.create(price_retail=price_retail + 100, cost_price=price_retail)
                #             VersionAttribute.objects.get_or_create(version=version, attribute=feature_height.children.all()[num])
                #             attribute_width.version = version
                #             attribute_width.save()
                #             attribute_length.version = version
                #             attribute_length.save()
                #
                price_retail = D(random.randint(1, 10000))
                version = product.versions.create(price_retail=price_retail + 100, cost_price=price_retail)

                VersionAttribute.objects.get_or_create(version=version, attribute=feature_width.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_length.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_height.children.all()[1])

                price_retail = D(random.randint(1, 10000))
                version = product.versions.create(price_retail=price_retail + 100, cost_price=price_retail)

                VersionAttribute.objects.get_or_create(version=version, attribute=feature_width.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_length.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_height.children.all()[2])

                price_retail = D(random.randint(1, 10000))
                version = product.versions.create(price_retail=price_retail + 100, cost_price=price_retail)

                VersionAttribute.objects.get_or_create(version=version, attribute=feature_width.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_length.children.all()[1])
                VersionAttribute.objects.get_or_create(version=version, attribute=feature_height.children.all()[3])

        save_category()
        save_product()
        create_feature()
        self.stdout.write('Successfully migrate date from db mysql soloha')