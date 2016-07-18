from django.contrib import admin
from apps.catalogue.widgets import MPTTFilteredSelectMultiple, MPTTModelMultipleChoiceField
from django.db import models
from oscar.core.loading import get_model
from feincms.admin import tree_editor
from django.forms import Textarea
from django import forms
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from import_export import resources
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ImportExportActionModelAdmin
from django.template import loader, Context
from import_export import fields, widgets
from filer.models.imagemodels import Image
import os
from widgets import ImageForeignKeyWidget, ImageManyToManyWidget


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


class ProductImageResource(resources.ModelResource):
    original = fields.Field(column_name='original', attribute='original',
                            widget=ImageForeignKeyWidget(model=Image, field='original_filename'))
    product_slug = fields.Field(column_name='product', attribute='product',
                                widget=widgets.ForeignKeyWidget(model=Product, field='slug'))

    class Meta:
        model = ProductImage
        fields = ('id', 'product_slug', 'original', 'caption', 'display_order', )
        export_order = fields

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
    class Meta:
        model = Feature
        skip_unchanged = True
        report_skipped = False
        exclude = ('lft', 'rght', 'tree_id', 'level', )


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('title', 'slug', 'parent', )
    list_filter = ('title', 'slug', 'parent')
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
                                   widget=widgets.ManyToManyWidget(model=Category, field='slug'))
    filters_slug = fields.Field(column_name='filters', attribute='filters',
                                widget=widgets.ManyToManyWidget(model=Feature, field='slug'))
    characteristics_slug = fields.Field(column_name='characteristics', attribute='characteristics',
                                        widget=widgets.ManyToManyWidget(model=Feature, field='slug'))

    class Meta:
        model = Product
        fields = ('id', 'title', 'slug', 'enable', 'h1', 'meta_title', 'meta_description', 'meta_keywords',
                  'description', 'categories_slug', 'filters_slug', 'characteristics_slug', 'product_class', )
        export_order = fields


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin, admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('title', 'thumb', 'date_updated', 'slug', 'get_product_class', 'structure', 'attribute_summary', 'pk')
    list_filter = ['structure', 'is_discountable']
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


class CategoryResource(resources.ModelResource):

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
