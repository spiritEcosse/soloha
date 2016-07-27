from itertools import chain
from django import forms
from django.conf import settings
from django.utils.encoding import smart_unicode, force_unicode
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
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from django.db.transaction import atomic, savepoint, savepoint_rollback, savepoint_commit  # noqa
from django.db.models import fields
from django.db.models.fields.related import ForeignKey

ProductImage = get_model('catalogue', 'ProductImage')


class MPTTModelChoiceIterator(forms.models.ModelChoiceIterator):
    def choice(self, obj):
        tree_id = getattr(obj, getattr(self.queryset.model._meta, 'tree_id_atrr', 'tree_id'), 0)
        left = getattr(obj, getattr(self.queryset.model._meta, 'left_atrr', 'lft'), 0)
        return super(MPTTModelChoiceIterator, self).choice(obj) + ((tree_id, left),)


class MPTTModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        level = getattr(obj, getattr(self.queryset.model._meta, 'level_attr', 'level'), 0)
        return u'%s %s' % ('-'*level, smart_unicode(obj))

    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return MPTTModelChoiceIterator(self)

    choices = property(_get_choices, forms.ChoiceField._set_choices)


class MPTTFilteredSelectMultiple(widgets.FilteredSelectMultiple):
    def __init__(self, verbose_name, is_stacked, attrs=None, choices=()):
        super(MPTTFilteredSelectMultiple, self).__init__(verbose_name, is_stacked, attrs, choices)

    def render_options(self, choices, selected_choices):
        """
        this is copy'n'pasted from django.forms.widgets Select(Widget)
        change to the for loop and render_option so they will unpack and use our extra tuple of mptt sort fields
        (if you pass in some default choices for this field, make sure they have the extra tuple too!)
        """
        def render_option(option_value, option_label, sort_fields):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_choices) and u' selected="selected"' or ''
            return u'<option value="%s" data-tree-id="%s" data-left-value="%s"%s>%s</option>' % (
                escape(option_value),
                sort_fields[0],
                sort_fields[1],
                selected_html,
                conditional_escape(force_unicode(option_label)),
            )
        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label, sort_fields in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label, sort_fields))
        return u'\n'.join(output)

    class Media:
        extend = False
        js = (settings.STATIC_ROOT + "js/mptt_m2m_selectbox.js",
              )

    class Media:
        extend = False
        js = (
            settings.STATIC_URL + "admin/js/core.js",
            settings.STATIC_URL + "admin/js/mptt_m2m_selectbox.js",
            settings.STATIC_URL + "admin/js/SelectFilter2.js",
        )


class ImageForeignKeyWidget(import_export_widgets.ForeignKeyWidget):
    def clean(self, value):
        val = super(import_export_widgets.ForeignKeyWidget, self).clean(value)
        image = Image.objects.filter(file=val).first()

        if image is None:
            image = Image.objects.create(file=val, original_filename=val)
        return image


class ImageManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def __init__(self, model, separator=None, field=None, *args, **kwargs):
        super(ImageManyToManyWidget, self).__init__(model, separator=separator, field=field, *args, **kwargs)
        self.obj = None

    def clean(self, value):
        product_images = []

        with transaction.atomic():
            ProductImage.objects.filter(product=self.obj).delete()

            if value:
                for display_order, val in enumerate(value.split(self.separator)):
                    product_image = ProductImage.objects.filter(product=self.obj, original__file=val).first()

                    if product_image is None:
                        image = Image.objects.filter(file=val).first()

                        if image is None:
                            image = Image.objects.create(file=val, original_filename=val)
                        product_image = ProductImage.objects.create(product=self.obj, original=image, display_order=display_order)
                    else:
                        product_image.display_order = display_order
                        product_image.save()
                    product_images.append(product_image)
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

        for field in self.intermediate_own_fields:
            result[field.name] = field.default if field.default else None

        intermediate_obj = self.rel_field.rel.through.objects.filter(**{
            self.rel_field.m2m_reverse_field_name(): related_obj,
            self.rel_field.m2m_field_name(): obj
        }).first()

        if intermediate_obj is not None:
            for field in self.intermediate_own_fields:
                result[field.name] = getattr(intermediate_obj, field.name)

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


class ManyToManyWidget(import_export_widgets.ManyToManyWidget):
    def __init__(self, *args, **kwargs):
        self.fields_all = kwargs.pop('fields_all', False)
        self.model_related_fields = kwargs.pop('model_related_fields', ())
        print kwargs
        print args
        super(ManyToManyWidget, self).__init__(*args, **kwargs)
        self.model_fields = []
        self.resource_field = None

        if self.fields_all is True:
            for field in self.model._meta.fields:
                if field is not self.model._meta.pk and not isinstance(field, fields.DateTimeField):
                    #ToDo: add and field.related_model != model
                    if isinstance(field, ForeignKey):
                        continue
                    self.model_fields.append(field)

    def clean(self, value):
        if not value:
            return self.model.objects.none()
        ids = filter(None, value.split(self.separator))
        objects = []

        with transaction.atomic():
            for id in ids:
                try:
                    objects.append(self.model.objects.get(**{self.field: id}))
                except ObjectDoesNotExist as e:
                    raise ValueError('{} {}: \'{}\'.'.format(e, self.model._meta.object_name, id))

        return objects

    def render(self, value, obj):
        if self.fields_all:
            if not value.all():
                return json.dumps([self.workpiece()])
            return json.dumps([self.object_representation(obj, related_obj) for related_obj in value.all()])

        super(ManyToManyWidget, self).render(value)

    def workpiece(self):
        result = {}

        for field in self.model_fields:
            result[field.name] = field.default() if not isinstance(field.default(), fields.NOT_PROVIDED) else ''
        return result

    def object_representation(self, obj, related_obj):
        result = {self.field: getattr(related_obj, self.field, None)}

        for field in self.model_fields:
            result[field.name] = field.default if field.default else None

        intermediate_obj = self.model.objects.filter(**{
            self.model.m2m_reverse_field_name(): related_obj,
            self.model.m2m_field_name(): obj
        }).first()

        if intermediate_obj is not None:
            for field in self.model_fields:
                result[field.name] = getattr(intermediate_obj, field.name)

        return result
