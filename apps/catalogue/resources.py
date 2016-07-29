from import_export import widgets as import_export_widgets
from import_export import resources, fields
import functools
import widgets
from django.db.models.fields.related import ForeignKey
from diff_match_patch import diff_match_patch
try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from diff_match_patch import diff_match_patch
from django.utils.safestring import mark_safe
from import_export.results import RowResult
from copy import deepcopy
from django.db import transaction
from django.db.transaction import TransactionManagementError
import logging  # isort:skip
#Todo change list import module
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
import traceback
from oscar.core.loading import get_model
from filer.models.imagemodels import Image

logging.getLogger(__name__).addHandler(NullHandler())

Feature = get_model('catalogue', 'Feature')
Category = get_model('catalogue', 'Category')
Product = get_model('catalogue', 'Product')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
ProductImage = get_model('catalogue', 'ProductImage')
ProductVersion = get_model('catalogue', 'ProductVersion')
VersionAttribute = get_model('catalogue', 'VersionAttribute')
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
    prefix = 'rel_'

    def __new__(cls, *args, **kwargs):
        obj = super(ModelResource, cls).__new__(cls, *args, **kwargs)

        for field in obj.get_fields():
            if isinstance(field.widget, widgets.IntermediateModelManyToManyWidget):
                field.widget.rel_field = obj._meta.model._meta.get_field_by_name(field.attribute)[0]

                field.widget.intermediate_own_fields = []

                for rel_field in field.widget.rel_field.rel.through._meta.fields:
                    if rel_field is not field.widget.rel_field.rel.through._meta.pk and not isinstance(rel_field, ForeignKey):
                        field.widget.intermediate_own_fields.append(rel_field)

        return obj

    @classmethod
    def widget_from_django_field(cls, f, default=import_export_widgets.Widget):
        """
        Returns the widget that would likely be associated with each
        Django type.
        """
        result = default
        internal_type = f.get_internal_type()
        if internal_type in ('ManyToManyField', ):
            result = functools.partial(widgets.IntermediateModelManyToManyWidget,
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
        field = Field(attribute=field_name, column_name=field_name, widget=FieldWidget(**widget_kwargs),
                      readonly=readonly)
        return field

    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    def copy_relation(self, obj):
        for field in self.get_fields():
            if isinstance(field.widget, widgets.IntermediateModelManyToManyWidget) \
                    or isinstance(field.widget, import_export_widgets.ManyToManyWidget) \
                    or isinstance(field.widget, widgets.ImageManyToManyWidget):
                setattr(obj, '{}{}'.format(self.prefix, field.column_name), self.export_field(field, obj))

    def import_row(self, row, instance_loader, dry_run=False, **kwargs):
        """
        Imports data from ``tablib.Dataset``. Refer to :doc:`import_workflow`
        for a more complete description of the whole import process.

        :param row: A ``dict`` of the row to import

        :param instance_loader: The instance loader to be used to load the row

        :param dry_run: If ``dry_run`` is set, or error occurs, transaction
            will be rolled back.
        """
        try:
            row_result = self.get_row_result_class()()
            instance, new = self.get_or_init_instance(instance_loader, row)
            if new:
                row_result.import_type = RowResult.IMPORT_TYPE_NEW
            else:
                row_result.import_type = RowResult.IMPORT_TYPE_UPDATE
            row_result.new_record = new
            row_result.object_repr = force_text(instance)
            row_result.object_id = instance.pk
            original = deepcopy(instance)
            self.copy_relation(original)

            if self.for_delete(row, instance):
                if new:
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                    row_result.diff = self.get_diff(None, None, dry_run)
                else:
                    row_result.import_type = RowResult.IMPORT_TYPE_DELETE
                    self.delete_instance(instance, dry_run)
                    row_result.diff = self.get_diff(original, None, dry_run)
            else:
                self.import_obj(instance, row, dry_run)
                if self.skip_row(instance, original):
                    row_result.import_type = RowResult.IMPORT_TYPE_SKIP
                else:
                    with transaction.atomic():
                        self.save_instance(instance, dry_run)
                    self.save_m2m(instance, row, dry_run)
                    # Add object info to RowResult for LogEntry
                    row_result.object_repr = force_text(instance)
                    row_result.object_id = instance.pk
                row_result.diff = self.get_diff(original, instance, dry_run)
        except Exception as e:
            # There is no point logging a transaction error for each row
            # when only the original error is likely to be relevant
            if not isinstance(e, TransactionManagementError):
                logging.exception(e)
            tb_info = traceback.format_exc()
            row_result.errors.append(self.get_error_result_class()(e, tb_info, row))
        return row_result

    def get_diff(self, original, current, dry_run=False):
        """
        Get diff between original and current object when ``import_data``
        is run.

        ``dry_run`` allows handling special cases when object is not saved
        to database (ie. m2m relationships).
        """
        data = []
        dmp = diff_match_patch()
        for field in self.get_fields():
            attr = '{}{}'.format(self.prefix, field.column_name)

            if hasattr(original, attr):
                v1 = getattr(original, attr)
            else:
                v1 = self.export_field(field, original) if original else ""

            v2 = self.export_field(field, current) if current else ""

            diff = dmp.diff_main(force_text(v1), force_text(v2))
            dmp.diff_cleanupSemantic(diff)
            html = dmp.diff_prettyHtml(diff)
            html = mark_safe(html)
            data.append(html)
        return data

    def save_m2m(self, obj, data, dry_run):
        """
        Saves m2m fields.

        Model instance need to have a primary key value before
        a many-to-many relationship can be used.
        """
        if not dry_run:
            for field in self.get_fields():
                field.widget.obj = obj

                if not isinstance(field.widget, import_export_widgets.ManyToManyWidget) \
                        and not isinstance(field.widget, widgets.ImageManyToManyWidget) \
                        and not isinstance(field.widget, widgets.IntermediateModelManyToManyWidget):
                    continue
                self.import_field(field, obj, data)


class FeatureResource(ModelResource):
    title = fields.Field(column_name='title', attribute='title', widget=widgets.CharWidget())
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'title', 'slug', 'parent', 'sort', 'bottom_line', 'top_line',)
        export_order = fields


class ProductVersionResource(ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'))
    attributes = Field(column_name='attributes', attribute='attributes',
                       widget=widgets.IntermediateModelManyToManyWidget(
                           model=Feature, field='slug'
                       ))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        fields = ('id', 'delete', 'product', 'price_retail', 'cost_price', 'attributes', )
        export_order = fields
        model = ProductVersion


class ProductFeatureResource(ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'))
    feature = fields.Field(column_name='feature', attribute='feature', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    image = fields.Field(column_name='image', attribute='image', widget=widgets.ImageManyToManyWidget(
        model=Image, field='original_filename'))
    product_with_images = fields.Field(column_name='product_with_images', attribute='product_with_images',
                                       widget=widgets.ManyToManyWidget(model=Product, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

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
    icon = fields.Field(column_name='icon', attribute='icon', widget=widgets.ImageManyToManyWidget(
        model=Image, field='original_filename'))
    image_banner = fields.Field(column_name='image_banner', attribute='image_banner', widget=widgets.ImageManyToManyWidget(
        model=Image, field='original_filename'))
    image = fields.Field(column_name='image', attribute='image', widget=widgets.ImageManyToManyWidget(
        model=Image, field='original_filename'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Category
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'link_banner', 'description', 'image', 'image_banner', 'icon', )
        export_order = fields


class ProductImageResource(ModelResource):
    original = fields.Field(column_name='original', attribute='original',
                            widget=widgets.ImageForeignKeyWidget(model=Image, field='original_filename'))
    product_slug = fields.Field(column_name='product', attribute='product',
                                widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = ProductImage
        #ToDo delete column to start list
        fields = ('id', 'product_slug', 'original', 'caption', 'display_order', 'delete', )
        export_order = fields

    def dehydrate_original(self, obj):
        if obj.original is not None:
            return obj.original.file.name
        else:
            return ''


class ProductRecommendationResource(ModelResource):
    primary = fields.Field(column_name='primary', attribute='primary', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug',
    ))
    recommendation = fields.Field(column_name='recommendation', attribute='recommendation',
                                  widget=import_export_widgets.ForeignKeyWidget(
                                      model=Product, field='slug',
                                  ))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

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
    images = fields.Field(column_name='images', attribute='images',
                          widget=widgets.ImageManyToManyWidget(model=ProductImage, field='original'))
    recommended_products = Field(column_name='recommended_products', attribute='recommended_products',
                                 widget=widgets.IntermediateModelManyToManyWidget(
                                     model=Product, field='slug',
                                 ))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Product
        fields = ('id', 'delete', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'categories_slug', 'filters_slug', 'characteristics_slug', 'product_class', 'images',
                  'recommended_products', )
        export_order = fields

    def dehydrate_images(self, obj):
        images = [prod_image.original.file.name for prod_image in obj.images.all() if prod_image.original]
        return ','.join(images)
