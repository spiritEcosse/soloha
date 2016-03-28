from django.contrib import admin
from oscar.apps.catalogue.admin import *  # noqa
from django import forms
from apps.catalogue.widgets import MPTTFilteredSelectMultiple, MPTTModelMultipleChoiceField
from mptt.forms import TreeNodeChoiceField
from django.db import models

Filter = get_model('catalogue', 'Filter')


class ProductForm(forms.ModelForm):
    filters = MPTTModelMultipleChoiceField(
        Filter.objects.all(),
        widget=MPTTFilteredSelectMultiple("filters", False, attrs={'rows': '10'})
    )

    class Meta:
        model = Filter
        fields = '__all__'


class ProductAdmin(ProductAdmin):
    # form = ProductForm
    formfield_overrides = {
        models.ManyToManyField: { 'widget': MPTTFilteredSelectMultiple("", False, attrs={'rows': '10'}) }
    }


class FilterAdmin(admin.ModelAdmin):
    pass


admin.site.register(Filter, FilterAdmin)
admin.site.unregister(Product)
admin.site.register(Product, ProductAdmin)
