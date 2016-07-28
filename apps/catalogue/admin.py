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
import logging  # isort:skip
#Todo change list import module
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
import traceback
from django.db.models.fields.related import ForeignKey

logging.getLogger(__name__).addHandler(NullHandler())

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text


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
ProductFeature = get_model('catalogue', 'ProductFeature')
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
        #ToDo delete column to start list
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


class FeatureResource(resources.ModelResource):
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'title', 'slug', 'parent', 'sort', 'bottom_line', 'top_line', )
        export_order = fields


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'slug', )
    resource_class = FeatureResource

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


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


class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'feature', 'product_date_updated', 'sort', 'info', 'product_enable',
                    'product_categories_to_str', 'product_partners_to_str', )
    list_filter = ('product__date_updated', 'product__enable', 'sort', 'product__stockrecords__partner',
                   'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )


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

    class Meta:
        model = Product
        #ToDo delete column to start list
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

    def before_import(self, dataset, dry_run, **kwargs):
        for field in self.get_fields():
            if isinstance(field.widget, widgets.IntermediateModelManyToManyWidget):
                field.widget.rel_field = self._meta.model._meta.get_field_by_name(field.attribute)[0]

                field.widget.intermediate_own_fields = []

                for rel_field in field.widget.rel_field.rel.through._meta.fields:
                    if rel_field is not field.widget.rel_field.rel.through._meta.pk and not isinstance(rel_field, ForeignKey):
                        field.widget.intermediate_own_fields.append(rel_field)


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
admin.site.register(ProductFeature, ProductFeatureAdmin)

admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
