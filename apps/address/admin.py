from django.contrib import admin
from apps.address.models import UserAddress, Country


class UserAddressAdmin(admin.ModelAdmin):
    readonly_fields = ('num_orders',)


class CountryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(UserAddress, UserAddressAdmin)
admin.site.register(Country, CountryAdmin)
