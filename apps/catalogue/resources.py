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
        images = []

        with transaction.atomic():
            for display_order, val in enumerate(value.split(self.separator)):
                product_image = ProductImage.objects.filter(product=self.obj, original__file=val).first()

                if product_image is None:
                    image = Image.objects.filter(file=val).first()

                    if image is None:
                        image = Image.objects.create(file=val, original_filename=val)
                    product_image = ProductImage.objects.create(product=self.obj, original=image, display_order=display_order)
                product_image.display_order = display_order
                product_image.save()
                images.append(product_image)
            ProductImage.objects.filter(product=self.obj).exclude(pk__in=[image.pk for image in images]).delete()
        return images


class IntermediateModelManyToManyWidget(import_export_widgets.ManyToManyWidget):

    def __init__(self, *args, **kwargs):
        self.rel = kwargs.pop('rel', None)
        super(IntermediateModelManyToManyWidget, self).__init__(*args,
                                                                **kwargs)

    def clean(self, value):
        ids = [item["uid"] for item in value]
        objects = self.model.objects.filter(**{
            '%s__in' % self.field: ids
        })
        return objects

    def render(self, value, obj):
        return [self.related_object_representation(obj, related_obj)
                for related_obj in value.all()]

    def related_object_representation(self, obj, related_obj):
        result = {
            "uid": related_obj.uid,
            "name": related_obj.name
        }
        if self.rel.through._meta.auto_created:
            return result
        intermediate_own_fields = [
            field for field in self.rel.through._meta.fields
            if field is not self.rel.through._meta.pk
            and not isinstance(field, ForeignKey)
        ]
        for field in intermediate_own_fields:
            result[field.name] = "foo"
        set_name = "{}_set".format(self.rel.through._meta.model_name)
        related_field_name = self.rel.to._meta.model_name
        intermediate_set = getattr(obj, set_name)
        intermediate_obj = intermediate_set.filter(**{
            related_field_name: related_obj
        }).first()
        for field in intermediate_own_fields:
            result[field.name] = getattr(intermediate_obj, field.name)
        return result


class Field(fields.Field):

    def is_m2m_with_intermediate_object(self, obj):
        field, _, _, m2m = obj._meta.get_field_by_name(self.attribute)
        return m2m and field.rel.through._meta.auto_created is False

    def get_intermediate_model(self, obj):
        field = obj._meta.get_field_by_name(self.attribute)[0]
        IntermediateModel = field.rel.through
        from_field_name = field.m2m_field_name()
        to_field_name = field.rel.to.__name__.lower()
        return IntermediateModel, from_field_name, to_field_name

    def remove_old_intermediates(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = \
            self.get_intermediate_model(obj)
        imported_ids = set(import_obj.pk for import_obj in self.clean(data))
        related_objects = getattr(obj, self.attribute).all()
        for related_object in related_objects:
            if related_object.pk not in imported_ids:
                queryset = IntermediateModel.objects.filter(**{
                    from_field_name: obj,
                    to_field_name: related_object
                })
                queryset.delete()

    def ensure_current_intermediates_created(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = \
            self.get_intermediate_model(obj)

        for related_object in self.clean(data):
            attributes = {from_field_name: obj, to_field_name: related_object}
            self.create_if_not_existing(IntermediateModel, attributes)

    @staticmethod
    def create_if_not_existing(IntermediateModel, attributes):
        # Use this instead of get_or_create in case we have duplicate
        # associations. (get_or_create would raise a DoesNotExist exception)
        if not IntermediateModel.objects.filter(**attributes).exists():
            IntermediateModel.objects.create(**attributes)

    def save(self, obj, data):
        """
        Cleans this field value and assign it to provided object.
        """
        if not self.readonly:
            if self.is_m2m_with_intermediate_object(obj):
                self.remove_old_intermediates(obj, data)
                self.ensure_current_intermediates_created(obj, data)
            else:
                setattr(obj, self.attribute, self.clean(data))

    def export(self, obj):
        """
        Returns value from the provided object converted to export
        representation.
        """
        value = self.get_value(obj)
        if value is None:
            return ""
        if isinstance(self.widget, IntermediateModelManyToManyWidget):
            return self.widget.render(value, obj)
        else:
            return self.widget.render(value)



class ModelResource(resources.ModelResource):

    @classmethod
    def widget_from_django_field(cls, f, default=import_export_widgets.Widget):
        """
        Returns the widget that would likely be associated with each
        Django type.
        """
        result = default
        internal_type = f.get_internal_type()
        if internal_type in ('ManyToManyField', ):
            result = functools.partial(IntermediateModelManyToManyWidget,
                                       model=f.rel.to, rel=f.rel)
        if internal_type in ('ForeignKey', 'OneToOneField', ):
            result = functools.partial(import_export_widgets.ForeignKeyWidget,
                                       model=f.rel.to)
        if internal_type in ('DecimalField', ):
            result = import_export_widgets.DecimalWidget
        if internal_type in ('DateTimeField', ):
            result = import_export_widgets.DateTimeWidget
        elif internal_type in ('DateField', ):
            result = import_export_widgets.DateWidget
        elif internal_type in ('IntegerField', 'PositiveIntegerField',
                               'PositiveSmallIntegerField',
                               'SmallIntegerField', 'AutoField'):
            result = import_export_widgets.IntegerWidget
        elif internal_type in ('BooleanField', 'NullBooleanField'):
            result = import_export_widgets.BooleanWidget
        return result


    @classmethod
    def field_from_django_field(self, field_name, django_field, readonly):
        """
        Returns a Resource Field instance for the given Django model field.
        """

        FieldWidget = self.widget_from_django_field(django_field)
        widget_kwargs = self.widget_kwargs_for_field(field_name)
        field = Field(attribute=field_name, column_name=field_name,
                      widget=FieldWidget(**widget_kwargs), readonly=readonly)
        return field