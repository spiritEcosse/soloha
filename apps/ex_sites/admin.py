from django.contrib.sites.admin import SiteAdmin
from django.contrib import admin
from oscar.core.loading import get_model

Info = get_model('sites', 'Info')
Site = get_model('sites', 'Site')


class InfoInline(admin.StackedInline):
    model = Info
    can_delete = False
    verbose_name_plural = 'info'


class InfoAdmin(SiteAdmin):
    inlines = (InfoInline, )


admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
