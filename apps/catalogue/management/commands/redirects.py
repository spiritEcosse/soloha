from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from oscar.core.utils import slugify
from django.db.models import F


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        current_site = Site.objects.get(pk=1)

        for category in Category.objects.all():
            old_path = '/{}/'.format(category.full_slug)
            new_path = category.get_absolute_url()
            print old_path
            print new_path
            Redirect.objects.create(site=current_site, old_path=old_path, new_path=new_path)

        print '\n end categories \n '

        for product in Product.objects.all():
            old_path = '/{}/{}'.format(product.categories.first().full_slug, product.slug)
            new_path = product.get_absolute_url()
            print old_path
            print new_path
            Redirect.objects.create(site=current_site, old_path=old_path, new_path=new_path)

        # Redirect.objects.all().update(new_path=F(slugify('new_path')))
        self.stdout.write('Successfully write redirects.')
