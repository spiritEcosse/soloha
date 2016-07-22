from django.contrib import admin
from apps.catalogue.widgets import MPTTFilteredSelectMultiple, MPTTModelMultipleChoiceField
from django.db import models
from oscar.core.loading import get_model
from feincms.admin import tree_editor
from django.forms import Textarea
from django import forms
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from import_export import resources as import_export_resources
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ImportExportActionModelAdmin
from django.template import loader, Context
from import_export import fields, widgets as import_export_widgets
from filer.models.imagemodels import Image
import os
import widgets
import resources
from import_export.results import RowResult
from copy import deepcopy
from django.db import transaction
from django.db.transaction import TransactionManagementError
import logging  # isort:skip
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
import traceback
from soloha.core import utils
from django.db.models.fields.related import ForeignKey

logging.getLogger(__name__).addHandler(NullHandler())

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from diff_match_patch import diff_match_patch
from django.utils.safestring import mark_safe

Feature = get_model('catalogue', 'Feature')
AttributeOption = get_model('catalogue', 'AttributeOption')
AttributeOptionGroup = get_model('catalogue', 'AttributeOptionGroup')
Category = get_model('catalogue', 'Category')
Option = get_model('catalogue', 'Option')
Product = get_model('catalogue', 'Product')
ProductAttribute = get_model('catalogue', 'ProductAttribute')
ProductAttributeValue = get_model('catalogue', 'ProductAttributeValue')
ProductClass = get_model('catalogue', 'ProductClass')
ProductImage = get_model('catalogue', 'ProductImage')
ProductRecommendation = get_model('catalogue', 'ProductRecommendation')
StockRecord = get_model('partner', 'StockRecord')
Info = get_model('sites', 'Info')


class ProductImageResource(import_export_resources.ModelResource):
    original = fields.Field(column_name='original', attribute='original',
                            widget=widgets.ImageForeignKeyWidget(model=Image, field='original_filename'))
    product_slug = fields.Field(column_name='product', attribute='product',
                                widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = ProductImage
        fields = ('id', 'product_slug', 'original', 'caption', 'display_order', 'delete', )
        export_order = fields

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    def dehydrate_original(self, obj):
        if obj.original is not None:
            return obj.original.file.name
        else:
            return ''


class ProductImageAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = ProductImageResource
    list_display = ('thumb', 'product', )

    def thumb(self, obj):
        return loader.get_template('admin/catalogue/product/thumb.html').render(Context({'image': obj.original}))
    thumb.allow_tags = True
    short_description = 'Image'


class FeatureResource(import_export_resources.ModelResource):
    class Meta:
        model = Feature
        skip_unchanged = True
        report_skipped = False
        exclude = ('lft', 'rght', 'tree_id', 'level', )


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'slug', )
    resource_class = FeatureResource


class AttributeInline(admin.TabularInline):
    model = ProductAttributeValue


class ProductRecommendationInline(admin.TabularInline):
    model = ProductRecommendation
    fk_name = 'primary'


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 2


class ProductClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'requires_shipping', 'track_stock')
    inlines = [ProductAttributeInline]


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class StockRecordInline(admin.TabularInline):
    model = StockRecord


class ProductForm(forms.ModelForm):
    filters = MPTTModelMultipleChoiceField(
        Feature.objects.all(),
        widget=MPTTFilteredSelectMultiple("Filters", False, attrs={'rows':'10'})
    )
    categories = MPTTModelMultipleChoiceField(
        Category.objects.all(),
        widget=MPTTFilteredSelectMultiple("Categories", False, attrs={'rows':'10'})
    )
    characteristics = MPTTModelMultipleChoiceField(
        Feature.objects.all(),
        widget=MPTTFilteredSelectMultiple("Characteristics", False, attrs={'rows':'10'})
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductResource(resources.ModelResource):
    categories_slug = fields.Field(column_name='categories', attribute='categories',
                                   widget=import_export_widgets.ManyToManyWidget(model=Category, field='slug'))
    filters_slug = fields.Field(column_name='filters', attribute='filters',
                                widget=import_export_widgets.ManyToManyWidget(model=Feature, field='slug'))
    characteristics_slug = fields.Field(column_name='characteristics', attribute='characteristics',
                                        widget=import_export_widgets.ManyToManyWidget(model=Feature, field='slug'))
    images = fields.Field(column_name='images', attribute='images',
                          widget=widgets.ImageManyToManyWidget(model=ProductImage, field='original'))
    recommended_products = resources.Field(column_name='recommended_products', attribute='recommended_products',
                                           widget=widgets.IntermediateModelManyToManyWidget(
                                               model=Product, field='slug',
                                           ))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())
    prefix = 'rel_'

    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'categories_slug', 'filters_slug', 'characteristics_slug', 'product_class', 'images',
                  'delete', 'recommended_products', )
        export_order = fields

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

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

    def dehydrate_images(self, obj):
        images = [prod_image.original.file.name for prod_image in obj.images.all() if prod_image.original]
        return ','.join(images)

    def copy_relation(self, obj):
        for field in self.get_fields():
            if isinstance(field.widget, widgets.IntermediateModelManyToManyWidget)\
                    or isinstance(field.widget, import_export_widgets.ManyToManyWidget)\
                    or isinstance(field.widget, widgets.ImageManyToManyWidget):
                setattr(obj, '{}{}'.format(self.prefix, field.column_name), self.export_field(field, obj))

    def before_import(self, dataset, dry_run, **kwargs):
        for field in self.get_fields():
            if isinstance(field.widget, widgets.IntermediateModelManyToManyWidget):
                field.widget.rel_field = self._meta.model._meta.get_field_by_name(field.attribute)[0]

                field.widget.intermediate_own_fields = []

                for rel_field in field.widget.rel_field.rel.through._meta.fields:
                    if rel_field is not field.widget.rel_field.rel.through._meta.pk and not isinstance(rel_field, ForeignKey):
                        field.widget.intermediate_own_fields.append(rel_field)

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
                row_result.diff = self.get_diff(original, instance, row, dry_run)
        except Exception as e:
            # There is no point logging a transaction error for each row
            # when only the original error is likely to be relevant
            if not isinstance(e, TransactionManagementError):
                logging.exception(e)
            tb_info = traceback.format_exc()
            row_result.errors.append(self.get_error_result_class()(e, tb_info, row))
        return row_result

    def get_diff(self, original, current, row, dry_run=False):
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


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('title', 'thumb', 'enable', 'date_updated', 'slug', 'get_product_class', 'structure', 'partner',
                    'attribute_summary', 'pk', )
    list_filter = ['enable', 'structure', 'is_discountable']
    inlines = [StockRecordInline, ProductRecommendationInline, ProductImageInline]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', )
    form = ProductForm
    resource_class = ProductResource

    def thumb(self, obj):
        return loader.get_template('admin/catalogue/product/thumb.html').render(Context({'image': obj.primary_image()}))
    thumb.allow_tags = True
    short_description = 'Image'

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return (
            qs.select_related(
                'product_class', 'parent'
            ).prefetch_related(
                'images',
                'attributes',
                'product_class__options',
                'categories__parent__parent__parent__parent',
                'stockrecords',
                'filters',
                'attributes',
                'characteristics',
            )
        )


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'product_class', 'type')
    prepopulated_fields = {"code": ("name", )}


class OptionAdmin(admin.ModelAdmin):
    pass


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'attribute', 'value')


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption


class AttributeOptionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'option_summary')
    inlines = [AttributeOptionInline, ]


class CategoryResource(import_export_resources.ModelResource):

    class Meta:
        model = Category
        exclude = ('lft', 'rght', 'tree_id', 'level', 'parent', )


class CategoryAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ("name", )}
    empty_value_display = '-empty-'
    list_display = ('indented_title', 'slug', 'parent', 'enable', 'sort', 'created')
    formfield_overrides = {
        models.ManyToManyField: {'widget': MPTTFilteredSelectMultiple("", False, attrs={'rows': '10'})},
        models.TextField: {'widget': Textarea(attrs={'cols': 40, 'rows': 4})},
    }
    list_filter = ('name', 'slug', 'parent', 'enable', 'sort', 'created')
    mptt_level_indent = 20
    search_fields = ('name', 'slug', )


class InfoInline(admin.StackedInline):
    model = Info
    can_delete = False
    verbose_name_plural = 'info'


class InfoAdmin(BaseSiteAdmin):
    inlines = (InfoInline, )


admin.site.register(ProductClass, ProductClassAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(AttributeOptionGroup, AttributeOptionGroupAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Feature, FeatureAdmin)

admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
