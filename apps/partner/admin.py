from django.contrib import admin
from oscar.apps.partner.admin import *  # noqa
from oscar.core.loading import get_model

Partner = get_model('partner', 'Partner')


class PartnerdAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', )
    search_fields = ('name', 'code',)


admin.site.unregister(Partner)
admin.site.register(Partner, PartnerdAdmin)
