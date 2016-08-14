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
        current_site = Site.objects.get(pk=1)

        for category in Category.objects.all():
            old_path = u'/{}/'.format(category.full_slug)
            new_path = category.get_absolute_url()
            print old_path
            print new_path
            Redirect.objects.create(site=current_site, old_path=old_path, new_path=new_path)

        print '\n end categories \n '

        count_products = Product.objects.count()

        for key, product in enumerate(Product.objects.all()):
            left_products = count_products - key

            print 'left products - {}'.format(left_products)

            if product.categories.first() is not None:
                old_path = u'/{}/{}'.format(product.categories.first().full_slug, product.slug)

                try:
                    new_path = product.get_absolute_url()
                except NoReverseMatch:
                    product.slug = slugify(product.slug)
                    product.save()
                    new_path = product.get_absolute_url()

                print old_path
                print new_path
                Redirect.objects.create(site=current_site, old_path=old_path, new_path=new_path)

        Redirect.objects.all().update(new_path=F(slugify('new_path')))
        Category.objects.all().update(slug=F(slugify('slug')))
        Product.objects.all().update(slug=F(slugify('slug')))

        self.stdout.write('Successfully write redirects.')
