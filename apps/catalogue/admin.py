from django.contrib import admin
from apps.catalogue.widgets import MPTTFilteredSelectMultiple, MPTTModelMultipleChoiceField
from django.db import models
from oscar.core.loading import get_model
from feincms.admin import tree_editor
from django.forms import Textarea
from django import forms
from django.contrib.admin import widgets
from django.contrib.sites.models import Site
from django.contrib.sites.admin import SiteAdmin as BaseSiteAdmin
from import_export import resources
from import_export.admin import ImportExportMixin, ImportExportModelAdmin, ImportExportActionModelAdmin
from django.template import loader, Context
from dal import autocomplete

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


class FeatureAdmin(tree_editor.TreeEditor):
    list_display = ('title', 'slug', 'parent', )
    list_filter = ('title', 'slug', 'parent')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'slug', )


class AttributeInline(admin.TabularInline):
    model = ProductAttributeValue


class ProductRecommendationForm(forms.ModelForm):
    class Meta:
        model = ProductRecommendation
        fields = '__all__'
        widgets = {
            'recommendation': autocomplete.ModelSelect2(url='product_recommendation_select2_fk')
        }


class ProductRecommendationInline(admin.TabularInline):
    model = ProductRecommendation
    fk_name = 'primary'
    form = ProductRecommendationForm


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
        widgets = {
            'parent': autocomplete.ModelSelect2(url='select2_fk')
        }
        exclude = ('name', )


class ProductAdmin(admin.ModelAdmin):
    save_as = True
    date_hierarchy = 'date_created'
    list_display = ('title', 'thumb', 'date_updated', 'slug', 'get_product_class', 'structure', 'attribute_summary', 'pk')
    list_filter = ['structure', 'is_discountable']
    inlines = [StockRecordInline, ProductRecommendationInline, ProductImageInline]
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', )
    form = ProductForm

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
                'recommended_products',
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


class CategoryAdmin(ImportExportModelAdmin, ImportExportActionModelAdmin, tree_editor.TreeEditor):
    prepopulated_fields = {'slug': ("name", )}
    list_display = ("name", 'slug', 'parent', 'enable', 'sort', 'created')
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
admin.site.register(ProductImage)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Feature, FeatureAdmin)

admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
