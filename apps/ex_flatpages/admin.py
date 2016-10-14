from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib import admin
import forms
from django.contrib.flatpages.models import FlatPage
from models import InfoPage


class InfoPageInline(admin.StackedInline):
    model = InfoPage
    can_delete = False
    verbose_name_plural = 'info'


class InfoPageAdmin(FlatPageAdmin):
    inlines = (InfoPageInline, )
    form = forms.FlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, InfoPageAdmin)
