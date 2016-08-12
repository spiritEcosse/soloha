from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from oscar.core.utils import slugify


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        current_site = Site.objects.get(pk=1)

        for category in Category.objects.all()[:5]:
            old_slug = '/{}'.format(category.full_slug)
            print old_slug
            # redirect = Redirect.objects.create(site=current_site, old_path=old_slug)
            # category.slug = slugify(category.slug)
            # category.save()
            # redirect.new_path = category.get_absolute_url()
            # redirect.save()
            # print redirect.new_path
            print category.get_absolute_url()

        # for product in Product.objects.all()[:3]:
        #     print '/{}/{}'.format(product.categories.first().full_slug, product.slug)
        #     print product.get_absolute_url()
            # Redirect.objects.create(site=current_site, old_path=product.slug, new_path=product.get_absolute_url())

        self.stdout.write('Successfully write redirects.')
