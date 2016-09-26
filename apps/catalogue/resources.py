from import_export import widgets as import_export_widgets
from import_export import resources, fields
import functools
import widgets
from django.db.models.fields.related import ForeignKey
from diff_match_patch import diff_match_patch
from django.utils.safestring import mark_safe
from import_export.results import RowResult
from copy import deepcopy
from django.db import transaction
from django.db.transaction import TransactionManagementError
import logging  # isort:skip
import traceback
from oscar.core.loading import get_model
from filer.models.imagemodels import Image
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
#Todo change list import module
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

Feature = get_model('catalogue', 'Feature')
Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
ProductImage = get_model('catalogue', 'ProductImage')
ProductFeature = get_model('catalogue', 'ProductFeature')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')


class Field(fields.Field):

    def is_m2m_with_intermediate_object(self, obj):
        field, _, _, m2m = obj._meta.get_field_by_name(self.attribute)
        return m2m and field.rel.through._meta.auto_created is False

    def get_intermediate_model(self, obj):
        field = obj._meta.get_field_by_name(self.attribute)[0]
        IntermediateModel = field.rel.through
        from_field_name = self.widget.rel_field.m2m_field_name()
        to_field_name = self.widget.rel_field.m2m_reverse_field_name()
        return IntermediateModel, from_field_name, to_field_name

    def remove_old_intermediates(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = self.get_intermediate_model(obj)
        imported_ids = set(import_obj[self.widget.field].pk for import_obj in self.clean(data))
        related_objects = getattr(obj, self.attribute).all()

        for related_object in related_objects:
            if related_object.pk not in imported_ids:
                queryset = IntermediateModel.objects.filter(**{
                    from_field_name: obj,
                    to_field_name: related_object
                })
                queryset.delete()

    def ensure_current_intermediates_created(self, obj, data):
        IntermediateModel, from_field_name, to_field_name = self.get_intermediate_model(obj)

        for related_object in self.clean(data):
            attributes_check = {from_field_name: obj, to_field_name: related_object[self.widget.field]}
            attributes = attributes_check.copy()

            for field in self.widget.intermediate_own_fields:
                attributes[field.name] = related_object[field.name]
            self.create_if_not_existing(IntermediateModel, attributes, attributes_check)

    def create_if_not_existing(self, IntermediateModel, attributes, attributes_check):
        # Use this instead of get_or_create in case we have duplicate
        # associations. (get_or_create would raise a DoesNotExist exception)

        if not IntermediateModel.objects.filter(**attributes_check).exists():
            IntermediateModel.objects.create(**attributes)
        else:
            intermediate_model = IntermediateModel.objects.filter(**attributes_check).first()

            for attribute, value in attributes.items():
                setattr(intermediate_model, attribute, value)

            intermediate_model.save()

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
        if isinstance(self.widget, widgets.IntermediateModelManyToManyWidget):
            return self.widget.render(value, obj)
        else:
            return self.widget.render(value)


class ModelResource(resources.ModelResource):
    delete = fields.Field(
        column_name='Delete this object ? (set 1 if True)',
        widget=import_export_widgets.BooleanWidget()
    )
    prefix = 'rel_'

    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class FeatureResource(ModelResource):
    title = fields.Field(column_name='title', attribute='title', widget=widgets.CharWidget())
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'title', 'slug', 'parent', 'sort', 'bottom_line', 'top_line',)
        export_order = fields


class ProductFeatureResource(ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'))
    feature = fields.Field(column_name='feature', attribute='feature', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    image = fields.Field(column_name='image', attribute='image', widget=widgets.ImageForeignKeyWidget(
        model=Image, field='original_filename'))
    product_with_images = fields.Field(column_name='product_with_images', attribute='product_with_images',
                                       widget=widgets.ManyToManyWidget(model=Product, field='slug'))

    class Meta:
        model = ProductFeature
        fields = ('id', 'delete', 'product', 'feature', 'sort', 'info', 'non_standard', 'image', 'product_with_images',)
        export_order = fields

    def dehydrate_image(self, obj):
        if obj.image is not None:
            return obj.image.file.name
        else:
            return ''


class CategoryResource(ModelResource):
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Category, field='slug'))
    icon = fields.Field(column_name='icon', attribute='icon', widget=widgets.ImageForeignKeyWidget(
        model=Image, field='original_filename'))
    image_banner = fields.Field(column_name='image_banner', attribute='image_banner', widget=widgets.ImageForeignKeyWidget(
        model=Image, field='original_filename'))
    image = fields.Field(column_name='image', attribute='image', widget=widgets.ImageForeignKeyWidget(
        model=Image, field='original_filename'))

    class Meta:
        model = Category
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'link_banner', 'description', 'image', 'image_banner', 'icon', )
        export_order = fields


class ProductImageResource(ModelResource):
    original = fields.Field(
        column_name='original', attribute='original',
        widget=widgets.ForeignKeyWidget(model=Image, field='original_filename')
    )
    product_slug = fields.Field(
        column_name='product', attribute='product',
        widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug')
    )

    class Meta:
        model = ProductImage
        fields = ('id', 'delete', 'product_slug', 'original', 'caption', 'display_order', )
        export_order = fields


class ProductRecommendationResource(ModelResource):
    primary = fields.Field(column_name='primary', attribute='primary', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug',
    ))
    recommendation = fields.Field(column_name='recommendation', attribute='recommendation',
                                  widget=import_export_widgets.ForeignKeyWidget(
                                      model=Product, field='slug',
                                  ))

    class Meta:
        model = ProductRecommendation
        fields = ('id', 'delete', 'primary', 'recommendation', 'ranking', )
        export_order = fields


class ProductResource(ModelResource):
    categories_slug = fields.Field(column_name='categories', attribute='categories',
                                   widget=widgets.ManyToManyWidget(model=Category, field='slug'))
    filters_slug = fields.Field(column_name='filters', attribute='filters',
                                widget=widgets.ManyToManyWidget(model=Feature, field='slug'))
    characteristics_slug = fields.Field(column_name='characteristics', attribute='characteristics',
                                        widget=widgets.ManyToManyWidget(model=Feature, field='slug'))
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'))

    class Meta:
        model = Product
        fields = ('id', 'delete', 'title', 'slug', 'enable', 'structure', 'parent', 'h1', 'meta_title',
                  'meta_description', 'meta_keywords', 'description', 'categories_slug', 'filters_slug', 'characteristics_slug',
                  'product_class', )
        export_order = fields
