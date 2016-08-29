from apps.catalogue.models import Product, Category, Feature
from django.core.management.base import BaseCommand
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.utils.text import slugify
from django.db.models import F
from django.core.urlresolvers import NoReverseMatch
import urllib2
from bs4 import BeautifulSoup
from django.core.exceptions import ObjectDoesNotExist
from urlparse import urlparse as method_urlparse
import urlparse


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
                self.save_filters(category, category_link)

            raise Exception('dfdf')

        self.stdout.write('Successfully write redirects.')

    def save_filters(self, category, absolute_link, slugs=[]):
        current_site = Site.objects.get(pk=1)

        category_page = urllib2.urlopen(absolute_link)
        category_page_soup = BeautifulSoup(category_page.read())
        filters = category_page_soup.select('#filters > [class=wrapp_options]')

        for filter_a in filters:
            option_name = filter_a.select_one('.option_name').text
            print option_name

            for value_label in filter_a.find_all('label', attrs={'class': None}):
                value_a = value_label.find('a')

                if value_a:
                    absolute_link = value_a.attrs['href']
                    relative_path_filter = absolute_link[21:]
                    print '--', value_a.text

                    try:
                        feature = Feature.objects.get(title__iexact=value_a.text, parent__title__iexact=option_name)
                    except ObjectDoesNotExist as e:
                        print e
                    else:
                        slugs.append(feature.slug)
                        filter_slug = '/'.join(set(slugs))
                        new_path = category.get_absolute_url(values={'filter_slug': filter_slug})
                        print '----(old, new) ', relative_path_filter, new_path
                        print '\n'

                        Redirect.objects.create(site=current_site, old_path=relative_path_filter, new_path=new_path)

                        filter_page = urllib2.urlopen(absolute_link)
                        filter_page_soup = BeautifulSoup(filter_page.read())
                        pages = filter_page_soup.select('#pagination_top .links a')
                        unique_pages = []

                        for page in pages:
                            relative_path_page = page.attrs['href'][21:]
                            unique_pages.append(relative_path_page)

                        if len(set(unique_pages)) == 10:
                            unique_pages = list(unique_pages)
                            filter_page = urllib2.urlopen('{}&page=11'.format(absolute_link))
                            filter_page_soup = BeautifulSoup(filter_page.read())
                            pages = filter_page_soup.select('#pagination_top .links a')

                            for page in pages:
                                relative_path_page = page.attrs['href'][21:]
                                unique_pages.append(relative_path_page)

                        for page in set(unique_pages):
                            url_page = method_urlparse(page)
                            page_numb = int(urlparse.parse_qs(url_page.query)['page'][0])
                            new_path = category.get_absolute_url(
                                values={'filter_slug': filter_slug, 'page': page_numb})
                            print '------(old, new)', page, new_path
                            print '\n'
                            Redirect.objects.create(site=current_site, old_path=page, new_path=new_path)

                        self.save_filters(category, absolute_link, slugs)
                print '\n'
        else:
            print 'final !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
            print slugs
            slugs = []
