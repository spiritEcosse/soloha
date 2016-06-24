from oscar.apps.order.admin import *  # noqa
QuickOrder = get_model('order', 'QuickOrder')


class QuickOrderAdmin(admin.ModelAdmin):
    model = QuickOrder


admin.site.register(QuickOrder, QuickOrderAdmin)
