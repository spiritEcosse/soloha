from django.contrib.sites.admin import SiteAdmin
from django.contrib import admin
from models import PhoneNumber, Info
from django.contrib.sites.models import Site


class InfoInline(admin.StackedInline):
    model = Info
    can_delete = False


class InfoAdmin(SiteAdmin):
    inlines = (InfoInline, )


class PhoneNumberAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Site)
admin.site.register(Site, InfoAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)
