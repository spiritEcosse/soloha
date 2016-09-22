from django.contrib import admin
from django.db import models
from oscar.core.loading import get_model
from django.forms import Textarea
from django import forms
from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import resources
import logging  # isort:skip
from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import forms
from django.db.models import Q
from django.db.models.query import Prefetch

#Todo change list import module
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

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
Partner = get_model('partner', 'Partner')
Info = get_model('sites', 'Info')


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Product.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
        return qs


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CategoriesAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Category.objects.all().only('pk', 'name', 'slug', )

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(slug__icontains=self.q))
        return qs


class FeatureAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeatureAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Feature.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
        return qs


class StockRecordInline(admin.StackedInline):
    model = StockRecord
    form = forms.StockRecordForm


class ProductFeatureInline(admin.StackedInline):
    model = ProductFeature
    form = forms.ProductFeatureForm


class AttributeInline(admin.TabularInline):
    model = ProductAttributeValue


class ProductRecommendationInline(admin.TabularInline):
    model = ProductRecommendation
    fk_name = 'primary'
    form = forms.ProductRecommendationForm


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 2


class AttributeOptionInline(admin.TabularInline):
    model = AttributeOption


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductImageAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = resources.ProductImageResource
    list_display = ('pk', 'thumb', 'product', 'product_date_updated', 'display_order', 'caption', 'product_enable',
                    'product_categories_to_str', 'product_partner', 'date_created', )
    list_filter = ('product__date_updated', 'date_created', 'product__enable', 'display_order',
                   'product__partner', 'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )
    form = forms.ProductImageForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title', 'slug', )
    resource_class = resources.FeatureResource
    form = forms.FeatureForm

    #ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class ProductClassAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'requires_shipping', 'track_stock')
    inlines = [ProductAttributeInline]


class ProductFeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'product', 'thumb', 'feature', 'product_date_updated', 'sort', 'info', 'product_enable',
                    'product_categories_to_str', 'product_partner', )
    list_filter = ('product__date_updated', 'product__enable', 'sort', 'product__partner',
                   'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )
    resource_class = resources.ProductFeatureResource
    form = forms.ProductFeatureForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'title', 'thumb', 'enable', 'date_updated', 'slug', 'categories_to_str', 'get_product_class',
                    'structure', 'partners_to_str', 'attribute_summary', )
    list_filter = ('enable', 'date_updated', 'partner', 'categories__name', 'structure', 'is_discountable', )
    inlines = (ProductImageInline, ProductRecommendationInline, ProductFeatureInline)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', 'id', )
    form = forms.ProductForm
    resource_class = resources.ProductResource
    list_select_related = ('product_class', 'partner',)
    list_attr = ('pk', 'title', 'enable', 'date_updated', 'slug', 'structure', 'product_class__name', )

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return qs.only(*self.list_attr).order_by('-date_updated', 'title').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.only('original', 'product')),
            Prefetch('images__original'),
            Prefetch('attribute_values'),
            Prefetch('attributes'),
            Prefetch('categories__parent__parent'),
            Prefetch('filters'),
            Prefetch('characteristics'),
        )


class ProductRecommendationAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'primary', 'product_enable', 'thumb', 'product_date_updated', 'product_categories_to_str',
                    'product_partner', 'recommendation', 'recommendation_thumb', 'ranking', )
    list_filter = ('primary__date_updated', 'primary__enable', 'ranking', 'primary__partner',
                   'primary__categories', )
    search_fields = ('primary__title', 'primary__slug', 'primary__pk', )
    resource_class = resources.ProductRecommendationResource
    form = forms.ProductRecommendationForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', 'product_class', 'type')
    prepopulated_fields = {"code": ("name", )}


class OptionAdmin(admin.ModelAdmin):
    pass


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('pk', 'product', 'attribute', 'value')


class AttributeOptionGroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'option_summary')
    inlines = [AttributeOptionInline, ]


class CategoryAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    prepopulated_fields = {'slug': ("name", )}
    list_display = ('pk', 'indented_title', 'slug', 'parent', 'enable', 'sort', 'created')
    list_filter = ('enable', 'created', 'sort', )
    formfield_overrides = {
        models.TextField: {'widget': Textarea()},
    }
    mptt_level_indent = 20
    search_fields = ('name', 'slug', 'id', )
    resource_class = resources.CategoryResource
    form = forms.CategoryForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


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
