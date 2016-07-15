# encoding: utf-8
from django.core.management.base import BaseCommand
from django.utils.text import slugify

##
## FancyImageModel is a plugin model holding a ImageField called "oldimage" and
## FilerImageField "image". It removed duplicates based on the basename of the original
## image. This may or may not work for you.

from apps.catalogue.models import ProductImage
from filer.models.imagemodels import Image
import os
from soloha.settings import MEDIA_ROOT

class Command(BaseCommand):
    args = ""
    help = ""

    def handle(self, *args, **options):
        fancies = ProductImage.objects.all()
        name_image_map = {}
        os.chdir(MEDIA_ROOT)

        for fancy in fancies:
            if fancy.original is None:
                if fancy.original_image:
                    if not os.path.exists(os.path.abspath(fancy.original_image.name)):
                        name = None
                    else:
                        name = os.path.basename(fancy.original_image.name)

                    print fancy.original_image, "needs migration"
                    print fancy.id
                    print name
                    print os.path.exists(os.path.abspath(fancy.original_image.name)), os.path.abspath(fancy.original_image.name)

                    if name is not None:
                        i = name_image_map.get(name)

                        if i is None:
                            i = Image(
                                file=fancy.original_image.name,
                                height=fancy.original_image.height,
                                width=fancy.original_image.width,
                                author="migrated",
                                original_filename=os.path.basename(fancy.original_image.name),
                                )
                            i.save()
                            name_image_map[name] = i
                        else:
                            print "already have ", name
                        fancy.original = i
                        fancy.save()

# alter table catalogue_productimage RENAME COLUMN original TO original_image;
# alter table catalogue_productimage ALTER COLUMN "original_image" drop not null;
# alter table "catalogue_productimage" ADD COLUMN "original_id" INTEGER REFERENCES "filer_image" ("file_ptr_id") DEFERRABLE INITIALLY DEFERRED;
