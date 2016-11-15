from itertools import chain
from django import forms
from django.conf import settings
from django.utils.html import escape, conditional_escape
from django.contrib.admin import widgets
from import_export import widgets as import_export_widgets
import os
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from filer.models.imagemodels import Image
from django.db import transaction
from oscar.core.loading import get_model
from import_export import resources, fields
from django.db.models.fields.related import ForeignKey
import functools
import json
from filer import settings as filer_settings
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from django.db.transaction import atomic, savepoint, savepoint_rollback, savepoint_commit  # noqa

ProductImage = get_model('catalogue', 'ProductImage')


def search_file(image_name, folder):
    """ Given a search path, find file with requested name """
    file = None

    for root, directories, file_names in os.walk(folder):
        for file_name in file_names:
            if file_name == image_name:
                if file is None:
                    file = os.path.join(root, file_name)
                else:
                    raise ValueError('The desired image {} is not unique. Duplicate - {}'.
                                     format(file, os.path.join(root, file_name)))
    return file


class MPTTModelChoiceIterator(forms.models.ModelChoiceIterator):
    def choice(self, obj):
        tree_id = getattr(obj, getattr(self.queryset.model._meta, 'tree_id_atrr', 'tree_id'), 0)
        left = getattr(obj, getattr(self.queryset.model._meta, 'left_atrr', 'lft'), 0)
        return super(MPTTModelChoiceIterator, self).choice(obj) + ((tree_id, left),)


class ImageForeignKeyWidget(import_export_widgets.ForeignKeyWidget):
    def clean(self, value):
        if value:
            if not os.path.dirname(value):
                folder = os.path.join(settings.MEDIA_ROOT, filer_settings.DEFAULT_FILER_STORAGES['public']['main']['UPLOAD_TO_PREFIX'])
                image = search_file(value, folder)
                value = '/'.join(os.path.relpath(image).split('/')[1:])

            image = self.model.objects.filter(file=value).first()

            if image is None:
                image = Image.objects.create(**{'file': value, self.field: value})
            return image


class ImageManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def __init__(self, model, separator=None, field=None, *args, **kwargs):
        super(ImageManyToManyWidget, self).__init__(model, separator=separator, field=field, *args, **kwargs)
        self.obj = None


    def clean(self, value):
        product_images = []

        if value:
            images = filter(None, value.split(self.separator))
            upload_to = filer_settings.DEFAULT_FILER_STORAGES['public']['main']['UPLOAD_TO_PREFIX']

            for display_order, val in enumerate(images):
                product_image = ProductImage.objects.filter(
                    product=self.obj, display_order=display_order
                ).first()

                current_path = os.getcwd()
                os.chdir(settings.MEDIA_ROOT)

                if not os.path.dirname(val):
                    folder = os.path.join(settings.MEDIA_ROOT, upload_to)
                    image = search_file(val, folder)

                    if image is not None:
                        val = os.path.relpath(image, start=settings.MEDIA_ROOT)
                else:
                    if not os.path.exists(os.path.abspath(val)):
                        raise ValueError('File "{}" does not exist.'.format(val))

                    if not os.path.isfile(os.path.abspath(val)):
                        raise ValueError('Is not file - "{}" '.format(val))

                os.chdir(current_path)

                image = Image.objects.filter(file=val).first()

                if image is None:
                    image = Image.objects.create(file=val, original_filename=val)

                if product_image is None:
                    product_image = ProductImage.objects.filter(product=self.obj, original__file=val).first()

                    if product_image is None:
                        product_image = ProductImage.objects.create(product=self.obj, original=image, display_order=display_order)
                    else:
                        product_image.display_order = display_order
                        product_image.save()
                    product_images.append(product_image)
                else:
                    product_image.original = image
                    product_image.save()
                    product_images.append(product_image)

            ProductImage.objects.filter(product=self.obj).exclude(pk__in=[obj.pk for obj in product_images]).delete()
        else:
            ProductImage.objects.filter(product=self.obj).delete()
        return product_images


class IntermediateModelManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def __init__(self, *args, **kwargs):
        super(IntermediateModelManyToManyWidget, self).__init__(*args, **kwargs)
        self.rel_field = None
        self.intermediate_own_fields = []

    def clean(self, value):
        items = json.loads(value)
        for key, item in enumerate(items[:]):
            items[key][self.field] = self.model.objects.get(**{self.field: item[self.field]})
        return items

    def render(self, value, obj):
        return json.dumps([self.related_object_representation(obj, related_obj) for related_obj in value.all()])

    def related_object_representation(self, obj, related_obj):
        result = {self.field: getattr(related_obj, self.field, None)}

        if self.rel_field.rel.through._meta.auto_created:
            return result

        intermediate_obj = self.rel_field.rel.through.objects.filter(**{
            self.rel_field.m2m_reverse_field_name(): related_obj,
            self.rel_field.m2m_field_name(): obj
        }).first()

        if intermediate_obj is not None:
            for field in self.intermediate_own_fields:
                result[field.name] = force_text(getattr(intermediate_obj, field.name))
        else:
            for field in self.intermediate_own_fields:
                result[field.name] = field.default if field.default else None

        return result


class CharWidget(import_export_widgets.Widget):
    """
    Widget for converting text fields.
    """

    def render(self, value):
        try:
            featured_value = force_text(int(float(value)))
        except ValueError:
            featured_value = force_text(value)
        return featured_value


class ForeignKeyWidget(import_export_widgets.ForeignKeyWidget):
    def clean(self, value):
        return super(ForeignKeyWidget, self).clean(value.strip())


class ManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return self.model.objects.none()

        ids = filter(None, value.split(self.separator))
        ids = map(lambda slug: slug.strip(), ids)
        return self.model.objects.filter(**{
            '%s__in' % self.field: ids
        })
