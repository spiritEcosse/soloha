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
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

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
from apps.catalogue.abstract_models import check_exist_image

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
Partner = get_model('partner', 'Partner')
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
    list_display = ('pk', 'thumb', 'product', 'product_date_updated', 'display_order', 'caption', 'product_enable',
                    'product_categories_to_str', 'product_partners_to_str', 'date_created', )
    list_filter = ('product__date_updated', 'date_created', 'product__enable', 'display_order',
                   'product__stockrecords__partner', 'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )


class FeatureResource(resources.ModelResource):
    title = fields.Field(column_name='title', attribute='title', widget=widgets.CharWidget())
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Feature
        fields = ('id', 'delete', 'title', 'slug', 'parent', 'sort', 'bottom_line', 'top_line', )
        export_order = fields


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'slug', 'parent', )
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
    list_display = ('pk', 'name', 'requires_shipping', 'track_stock')
    inlines = [ProductAttributeInline]


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductFeatureResource(resources.ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'))
    feature = fields.Field(column_name='feature', attribute='feature', widget=import_export_widgets.ForeignKeyWidget(
        model=Feature, field='slug'))
    image = fields.Field(column_name='image', attribute='image', widget=widgets.ImageForeignKeyWidget(
        model=Image, field='original_filename'))
    product_with_images = fields.Field(column_name='product_with_images', attribute='product_with_images',
                                       widget=widgets.ManyToManyWidget(model=Product, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = ProductFeature
        fields = ('id', 'delete', 'product', 'feature', 'sort', 'info', 'non_standard', 'image', 'product_with_images',)
        export_order = fields

    # ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    def dehydrate_image(self, obj):
        if obj.image is not None:
            return obj.image.file.name
        else:
            return ''


class ProductFeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'product', 'thumb', 'feature', 'product_date_updated', 'sort', 'info', 'product_enable',
                    'product_categories_to_str', 'product_partners_to_str', )
    list_filter = ('product__date_updated', 'product__enable', 'sort', 'product__stockrecords__partner',
                   'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )
    resource_class = ProductFeatureResource


class StockRecordInline(admin.TabularInline):
    model = StockRecord


class ProductForm(forms.ModelForm):
    filters = MPTTModelMultipleChoiceField(
        Feature.objects.all(), required=False,
        widget=MPTTFilteredSelectMultiple("Filters", False, attrs={'rows':'10'})
    )
    categories = MPTTModelMultipleChoiceField(
        Category.objects.all(), required=False,
        widget=MPTTFilteredSelectMultiple("Categories", False, attrs={'rows':'10'})
    )
    characteristics = MPTTModelMultipleChoiceField(
        Feature.objects.all(), required=False,
        widget=MPTTFilteredSelectMultiple("Characteristics", False, attrs={'rows':'10'})
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductResource(resources.ModelResource):
    categories_slug = fields.Field(column_name='categories', attribute='categories',
                                   widget=widgets.ManyToManyWidget(model=Category, field='slug'))
    filters_slug = fields.Field(column_name='filters', attribute='filters',
                                widget=widgets.ManyToManyWidget(model=Feature, field='slug'))
    characteristics_slug = fields.Field(column_name='characteristics', attribute='characteristics',
                                        widget=widgets.ManyToManyWidget(model=Feature, field='slug'))
    images = fields.Field(column_name='images', attribute='images',
                          widget=widgets.ImageManyToManyWidget(model=ProductImage, field='original'))
    recommended_products = resources.Field(column_name='recommended_products', attribute='recommended_products',
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
    list_display = ('pk', 'title', 'thumb', 'enable', 'date_updated', 'slug', 'categories_to_str', 'get_product_class',
                    'structure', 'partners_to_str', 'attribute_summary', )
    list_filter = ('enable', 'stockrecords__partner', 'categories', 'structure', 'is_discountable', )
    inlines = [StockRecordInline, ProductRecommendationInline, ProductImageInline]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', )
    form = ProductForm
    resource_class = ProductResource

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


class ProductRecommendationResource(resources.ModelResource):
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

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class ProductRecommendationAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'primary', 'product_enable', 'thumb', 'product_date_updated', 'product_categories_to_str',
                    'product_partners_to_str', 'recommendation', 'recommendation_thumb', 'ranking', )
    list_filter = ('primary__date_updated', 'primary__enable', 'ranking', 'primary__stockrecords__partner',
                   'primary__categories', )
    search_fields = ('primary__title', 'primary__slug', 'primary__pk', )
    resource_class = ProductRecommendationResource


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', 'product_class', 'type')
    prepopulated_fields = {"code": ("name", )}


class OptionAdmin(admin.ModelAdmin):
    pass


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'attribute', 'value')


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption


class AttributeOptionGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'option_summary')
    inlines = [AttributeOptionInline, ]


class CategoryResource(resources.ModelResource):
    parent = fields.Field(attribute='parent', column_name='parent', widget=import_export_widgets.ForeignKeyWidget(
        model=Category, field='slug'))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = Category
        #Todo add: 'icon', 'image_banner', 'image'
        fields = ('id', 'delete', 'enable', 'name', 'slug', 'parent', 'sort', 'meta_title', 'h1', 'meta_description',
                  'meta_keywords', 'link_banner', 'description', )
        export_order = fields

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class CategoryAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ("name", )}
    list_display = ('pk', 'indented_title', 'slug', 'parent', 'enable', 'sort', 'created')
    list_filter = ('enable', 'created', 'sort', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': MPTTFilteredSelectMultiple("", False, attrs={'rows': '10'})},
        models.TextField: {'widget': Textarea(attrs={'cols': 40, 'rows': 4})},
    }
    mptt_level_indent = 20
    search_fields = ('name', 'slug', )
    resource_class = CategoryResource


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
admin.site.register(ProductRecommendation, ProductRecommendationAdmin)

admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
