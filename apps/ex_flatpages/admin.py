from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib import admin
from oscar.core.loading import get_model
import forms

InfoPage = get_model('flatpages', 'InfoPage')
FlatPage = get_model('flatpages', 'FlatPage')


class InfoPageInline(admin.StackedInline):
    model = InfoPage
    can_delete = False
    verbose_name_plural = 'info'


class InfoPageAdmin(FlatPageAdmin):
    inlines = (InfoPageInline, )
    form = forms.FlatPageForm


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, InfoPageAdmin)
