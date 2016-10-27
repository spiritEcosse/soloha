from apps.catalogue.models import Product, Category
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from filer.models.imagemodels import Image
from apps.catalogue.models import ProductImage, Product
from django.core.files import File


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

        for key, product in enumerate(products):
            left_products = products.count() - key
            soup = BeautifulSoup(product.description, 'html5lib')

            tds = list(zip(*[iter(soup.table.find_all('tr'))] * 2))

            for links, names in tds:
                images = list(zip(links, names))

                for image, name in images:
                    print image.img, name.string

                    filename = '809.jpg'
                    filepath = '/home/igor/web/www/soloha/media/data/DisVita/Cosmic/'
                    user = User.objects.get(pk=1)

                    with open(filepath, "rb") as file_path:
                        file_obj = File(file_path, name=filename)
                        image = Image.objects.create(owner=user, original_filename=filename, file=file_obj)
                        ProductImage.objects.create(original=image, product=product)

            print 'left products - {}'.format(left_products)
            raise Exception('df')

        self.stdout.write('Successfully write images.')
