from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from oscar.core.utils import slugify
from django.db.models import F
from django.core.urlresolvers import NoReverseMatch
import urllib2
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        url = 'http://soloha.kiev.ua'
        main_page = urllib2.urlopen(url)
        soup_main_page = BeautifulSoup(main_page.read())
        categories = soup_main_page.find(id='topnav2')

        for category_a in categories.find_all('a')[1:]:
            category_link = category_a.attrs['href']

            relative_path = category_link[21:]

            try:
                redirect = Redirect.objects.get(old_path=relative_path)
                category_slug = redirect.new_path.split('/')[-2]
                category = Category.objects.get(slug=category_slug)
            except ObjectDoesNotExist as e:
                print e
            else:
                category_page = urllib2.urlopen(category_link)
                category_page_soup = BeautifulSoup(category_page.read())
                category_page_soup = category_page_soup.find(id='filters')

                for category_filter_a in category_page_soup.find_all('a'):
                    relative_path_filter_a = category_filter_a.attrs['href'][21:]
                    print relative_path_filter_a, category_filter_a.text
                    parent = category_filter_a.find_parents("div", 'class="wrapp_options"')
                    print parent.find('div', 'class="option_name"')

            raise Exception('dfdf')

        self.stdout.write('Successfully write redirects.')
