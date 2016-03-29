from django import forms

from django.contrib.admin import widgets

from oscar.apps.catalogue.abstract_models import AbstractProduct
from .models import  Product
from apps.catalogue.widgets import MPTTModelMultipleChoiceField
from apps.catalogue.widgets import MPTTFilteredSelectMultiple

from oscar.core.loading import get_model

from django.contrib import admin

from oscar.apps.catalogue.admin import ProductAdmin as CoreProductAdmin 

from django.db import models

# ProductFilter = get_model('catalogue', 'ProductFilter')
#
# class ProductForm(forms.ModelForm):
#     filters = MPTTModelMultipleChoiceField(
#                     ProductFilter.objects.all(),
#                     widget = MPTTFilteredSelectMultiple("Products",False,attrs={'rows':'10'})
#                 )
#     class Meta:
#         model= ProductFilter
#         fields = '__all__'
#
# class ProductAdmin(CoreProductAdmin):
# 	formfield_overrides = {
#         models.ManyToManyField: {'widget': widgets.FilteredSelectMultiple('', False, attrs={'size': '10'})},
# }


# admin.site.register(Product)

# class ProductFilterRelationshipInline(admin.TabularInline):
#     model = FeedCategoryRelationship
#     extra = 1

# class ProductAdmin(admin.ModelAdmin):
#     inlines = (ProductFilterRelationshipInline,)

# class FilterAdmin(admin.ModelAdmin):
#     inlines = (ProductFilterRelationshipInline,)
#     prepopulated_fields = { "slug": ("name",) }


# admin.site.register(ProductFilterRelationship, ProductFilterRelationshipInline)
from oscar.apps.catalogue.admin import *  # noqa
