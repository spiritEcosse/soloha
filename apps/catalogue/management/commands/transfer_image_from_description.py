# -*- coding: utf-8 -*-

from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from apps.catalogue.models import ProductImage, Product
import re
from django.core.files import File
from soloha import settings
from django.contrib.auth.models import User
from filer.models.imagemodels import Image
import os
from django.db import IntegrityError
from django.core.exceptions import MultipleObjectsReturned


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """
        products = Product.objects.filter(categories__slug__in=[
            'mebelnie-tkani-dlay-obshivki-divanov', 'mebelnie-tkani', 'naturalne_koga', 'avtomobile_koga']
        )
        user = User.objects.first()

        def save_images(table):
            tds = list(zip(*[iter(table.find_all('tr'))] * 2))

            for links, names in tds:
                images = list(zip(links.find_all('td'), names.find_all('td')))

                for image, name in images:
                    if image.img is not None:
                        image_source = image.img.get('src', None)
                        image_name = re.sub(r'\n\s+', ' ', name.text).strip()
                        print image_source, image_name

                        if image_source is not None:
                            image_source = image_source.replace('http://soloha.kiev.ua/image/', '')
                            image_source = image_source.replace('/image/', '', 1)

                            try:
                                with open(os.path.join(settings.MEDIA_ROOT, image_source), "rb") as file_path:
                                    filename = image_source.split('/')[-1]
                                    file_obj = File(file_path, name=filename)

                                    try:
                                        image, created = Image.objects.get_or_create(original_filename=filename)
                                    except MultipleObjectsReturned as message:
                                        print [(image, image.file.path) for image in Image.objects.filter(original_filename=filename)]
                                        raise Exception(message)
                                    else:
                                        if created:
                                            image.file = file_obj
                                            image.owner = user
                                            image.name = filename
                                            image.save()

                                        fields = {
                                            'original': image, 'product': product
                                        }
                                        created = False

                                        try:
                                            product_image, created = ProductImage.objects.get_or_create(**fields)
                                        except IntegrityError:
                                            product_image = ProductImage.objects.filter(product=product).order_by(
                                                'display_order').last()
                                            fields['display_order'] = product_image.display_order + 1
                                            product_image, created = ProductImage.objects.get_or_create(**fields)
                                        except MultipleObjectsReturned as message:
                                            print '\nMultipleObjectsReturned'
                                            print image.file.path
                                            print product, product.pk

                                        if created:
                                            product_image.caption = image_name or os.path.splitext(filename)[0]
                                            product_image.save()
                            except IOError as message:
                                print message

        for key, product in enumerate(products):
            left_products = products.count() - key
            print product.pk, product.slug
            soup = BeautifulSoup(product.description, 'html5lib')

            for table in soup.find_all('table'):
                save_images(table)
                table.extract()

            text = soup.find(text=re.compile(u"ИЗОБРАЖЕНИЯ ТКАНЕЙ"))

            if text is not None:
                text.parent.parent.next_sibling.next_sibling.extract()
                text.parent.parent.extract()

            text = soup.find(text=re.compile(u'в более отдаленном'))

            if text is not None:
                text.parent.parent.parent.parent.next_sibling.next_sibling.extract()
                text.parent.parent.parent.parent.extract()

            description = soup.prettify().strip()
            product.description = description
            product.save()

            print 'left products - {}'.format(left_products)

        self.stdout.write('Successfully write images.')
