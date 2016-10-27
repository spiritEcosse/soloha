from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from oscar.core.utils import slugify
from django.db.models import F
from django.core.urlresolvers import NoReverseMatch


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        products = Product.objects.all()

        for key, product in enumerate(products):
            left_products = products.count() - key

            print 'left products - {}'.format(left_products)

        self.stdout.write('Successfully write images.')
