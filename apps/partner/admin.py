from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
from oscar.apps.partner.admin import *  # noqa
from dal import autocomplete
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import resources

Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')


class StockRecordAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = resources.StockRecordResource
    list_display = ('pk', 'product',
                    # Todo uncomment after delete field - product
                    # 'thumb', 'product_enable', 'product_partner', 'product_categories_to_str',
                    'price_currency', 'price_excl_tax',
                    'price_retail', 'cost_price', 'num_in_stock', 'num_allocated', 'low_stock_threshold',)
    search_fields = ('product__slug', 'product__title', 'product__pk', )
    list_filter = ('date_created', 'date_updated', 'product__enable', 'product__date_updated', 'product__categories',
                   'product__partner', )


class PartnerdAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', )
    search_fields = ('name', 'code',)


class PartnerAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PartnerAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Partner.objects.all().only('pk', 'name', 'code', )

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q) | Q(code__icontains=self.q))

        return qs


admin.site.unregister(Partner)
admin.site.register(Partner, PartnerdAdmin)
admin.site.unregister(StockRecord)
admin.site.register(StockRecord, StockRecordAdmin)
