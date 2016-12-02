from django.contrib import admin
from django.forms import Textarea
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.db.models.query import Prefetch

from mptt.admin import DraggableMPTTAdmin
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
import logging
from dal import autocomplete

from apps.catalogue import resources, models as catalogue_models, forms as catalogue_forms
from apps.partner import models as partner_models, forms as partner_forms

logging.getLogger(__name__).addHandler(logging.NullHandler())


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProductAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = catalogue_models.Product.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
            else:
                qs = qs.filter(Q(pk=self.q))

        return qs


class CategoriesAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CategoriesAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = catalogue_models.Category.objects.all().only('pk', 'name', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(name__icontains=self.q) | Q(slug__icontains=self.q))
            else:
                qs = qs.filter(Q(pk=self.q))

        return qs


class FeatureAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FeatureAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = catalogue_models.Feature.objects.all().only('pk', 'title', 'slug', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(title__icontains=self.q) | Q(slug__icontains=self.q))
            else:
                qs = qs.filter(Q(pk=self.q))

        return qs


class StockRecordInline(admin.StackedInline):
    model = partner_models.StockRecord
    form = partner_forms.StockRecordForm


class ProductFeatureInline(admin.StackedInline):
    model = catalogue_models.ProductFeature
    form = catalogue_forms.ProductFeatureForm


class AttributeInline(admin.TabularInline):
    model = catalogue_models.ProductAttributeValue


class ProductRecommendationInline(admin.TabularInline):
    model = catalogue_models.ProductRecommendation
    fk_name = 'primary'
    form = catalogue_forms.ProductRecommendationForm


class ProductAttributeInline(admin.TabularInline):
    model = catalogue_models.ProductAttribute
    extra = 2


class AttributeOptionInline(admin.TabularInline):
    model = catalogue_models.AttributeOption


class ProductImageInline(admin.TabularInline):
    model = catalogue_models.ProductImage


class ProductImageAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = resources.ProductImageResource
    list_display = ('pk', 'thumb', 'product', 'product_slug', 'product_enable', 'product_date_updated', 'display_order',
                    'caption', 'product_categories_to_str', 'product_partner', 'date_created', )
    list_filter = ('product__date_updated', 'date_created', 'product__enable', 'display_order',
                   'product__partner', 'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )
    form = catalogue_forms.ProductImageForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class FeatureAdmin(ImportExportMixin, ImportExportActionModelAdmin, DraggableMPTTAdmin):
    list_display = ('pk', 'indented_title', 'slug', 'parent', )
    list_filter = ('created', )
    search_fields = ('title', 'slug', )
    resource_class = resources.FeatureResource
    form = catalogue_forms.FeatureForm

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
    list_display = ('pk', 'product', 'product_slug', 'thumb', 'feature', 'product_date_updated', 'sort', 'info', 'product_enable',
                    'product_categories_to_str', 'product_partner', )
    list_filter = ('product__date_updated', 'product__enable', 'sort', 'product__partner',
                   'product__categories', )
    search_fields = ('product__title', 'product__slug', 'product__pk', )
    resource_class = resources.ProductFeatureResource
    form = catalogue_forms.ProductFeatureForm

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")


class ProductAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'title', 'thumb', 'enable', 'date_updated', 'slug', 'categories_to_str', 'get_product_class',
                    'structure', 'partners_to_str', 'attribute_summary', )
    list_filter = ('enable', 'date_updated', 'partner', 'categories__name', 'structure', 'is_discountable', )
    inlines = (StockRecordInline, ProductImageInline, ProductRecommendationInline, ProductFeatureInline)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('upc', 'title', 'slug', 'id', )
    form = catalogue_forms.ProductForm
    resource_class = resources.ProductResource
    list_select_related = ('product_class', 'partner',)
    list_attr = ('pk', 'title', 'enable', 'date_updated', 'slug', 'structure', 'product_class__name', 'partner', )

    class Media:
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
              "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js")

    def get_queryset(self, request):
        qs = super(ProductAdmin, self).get_queryset(request)
        return qs.only(*self.list_attr).order_by('-date_updated', 'title').prefetch_related(
            Prefetch('images', queryset=catalogue_models.ProductImage.objects.only('original', 'product')),
            Prefetch('images__original'),
            Prefetch('attribute_values'),
            Prefetch('attributes'),
            Prefetch('categories__parent__parent'),
            Prefetch('filters'),
            Prefetch('characteristics'),
        )


class ProductRecommendationAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    list_display = ('pk', 'primary', 'product_slug', 'product_enable', 'thumb', 'product_date_updated',
                    'product_categories_to_str', 'product_partner', 'recommendation', 'recommendation_thumb', 'ranking',)
    list_filter = ('primary__date_updated', 'primary__enable', 'ranking', 'primary__partner',
                   'primary__categories', )
    search_fields = ('primary__title', 'primary__slug', 'primary__pk', )
    resource_class = resources.ProductRecommendationResource
    form = catalogue_forms.ProductRecommendationForm

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
        catalogue_models.TextField: {'widget': Textarea()},
    }
    mptt_level_indent = 20
    search_fields = ('name', 'slug', 'id', )
    resource_class = resources.CategoryResource
    form = catalogue_forms.CategoryForm

    class Media:
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/css/select2.min.css",
            "https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.3/js/select2.min.js"
        )


admin.site.register(catalogue_models.ProductClass, ProductClassAdmin)
admin.site.register(catalogue_models.Product, ProductAdmin)
admin.site.register(catalogue_models.ProductAttribute, ProductAttributeAdmin)
admin.site.register(catalogue_models.ProductAttributeValue, ProductAttributeValueAdmin)
admin.site.register(catalogue_models.AttributeOptionGroup, AttributeOptionGroupAdmin)
admin.site.register(catalogue_models.Option, OptionAdmin)
admin.site.register(catalogue_models.ProductImage, ProductImageAdmin)
admin.site.register(catalogue_models.Category, CategoryAdmin)
admin.site.register(catalogue_models.Feature, FeatureAdmin)
admin.site.register(catalogue_models.ProductFeature, ProductFeatureAdmin)
admin.site.register(catalogue_models.ProductRecommendation, ProductRecommendationAdmin)
