from django.contrib import admin
from apps.catalogue.widgets import MPTTFilteredSelectMultiple, MPTTModelMultipleChoiceField
from django.db import models
from oscar.core.loading import get_model
from feincms.admin import tree_editor
from django.forms import Textarea
from django import forms
from django.contrib.admin import widgets


Filter = get_model('catalogue', 'Filter')
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


class FilterAdmin(tree_editor.TreeEditor):
    list_display = ('title', 'slug', 'parent', )
    list_filter = ('title', 'slug', 'parent')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'slug', )


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


class ProductForm(forms.ModelForm):
    filters = MPTTModelMultipleChoiceField(
                    Filter.objects.all(),
                    widget=MPTTFilteredSelectMultiple("Filters", False, attrs={'rows':'10'})
                )
    categories = MPTTModelMultipleChoiceField(
                    Category.objects.all(),
                    widget=MPTTFilteredSelectMultiple("Categories", False, attrs={'rows':'10'})
                )

    class Meta:
        model = Filter
        fields = '__all__'


class ProductAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_created'
    list_display = ('get_title', 'upc', 'get_product_class', 'structure',
                    'attribute_summary', 'date_created')
    list_filter = ['structure', 'is_discountable']
    inlines = [AttributeInline, ProductRecommendationInline]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', )
    form = ProductForm

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return (
            qs
                .select_related('product_class', 'parent')
                .prefetch_related(
                'attribute_values',
                'attribute_values__attribute'))


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


class CategoryAdmin(tree_editor.TreeEditor):
    prepopulated_fields = {'slug': ("name", )}
    list_display = ("name", 'slug', 'parent', 'enable', 'sort', 'created')
    formfield_overrides = {
        models.ManyToManyField: {'widget': MPTTFilteredSelectMultiple("", False, attrs={'rows': '10'})},
        models.TextField: {'widget': Textarea(attrs={'cols': 40, 'rows': 4})},
    }
    list_filter = ('name', 'slug', 'parent', 'enable', 'sort', 'created')
    mptt_level_indent = 20
    search_fields = ('name', 'slug', )


admin.site.register(ProductClass, ProductClassAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttribute, ProductAttributeAdmin)
admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(AttributeOptionGroup, AttributeOptionGroupAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(ProductImage)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Filter, FilterAdmin)
