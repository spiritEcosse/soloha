from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib import admin
from apps.ex_flatpages import forms
from django.contrib.flatpages.models import FlatPage
from apps.ex_flatpages.models import InfoPage


class InfoPageInline(admin.StackedInline):
    model = InfoPage
    can_delete = False
    verbose_name_plural = 'info'


class InfoPageAdmin(FlatPageAdmin):
    inlines = (InfoPageInline, )
    form = forms.FlatPageForm
    prepopulated_fields = {"url": ("title", )}


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, InfoPageAdmin)
