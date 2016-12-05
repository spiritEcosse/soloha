from django.contrib import admin

from apps.payment.models import Source, Transaction, SourceType, Bankcard


class SourceAdmin(admin.ModelAdmin):
    list_display = ('order', 'source_type', 'amount_allocated', 'amount_debited', 'balance', 'reference')


class BankcardAdmin(admin.ModelAdmin):
    list_display = ('number', 'card_type', 'expiry_month')


admin.site.register(Source, SourceAdmin)
admin.site.register(SourceType)
admin.site.register(Transaction)
admin.site.register(Bankcard, BankcardAdmin)
