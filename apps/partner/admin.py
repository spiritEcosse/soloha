from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
from dal import autocomplete
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import resources
from django.contrib import admin
from models import Partner, StockRecord
import forms as partner_forms


class PartnerAutocomplete(autocomplete.Select2QuerySetView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PartnerAutocomplete, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = Partner.objects.all().only('pk', 'name', 'code', )

        if self.q:
            try:
                self.q = int(self.q)
            except ValueError:
                qs = qs.filter(Q(name__icontains=self.q) | Q(code__icontains=self.q))
            else:
                qs = qs.filter(Q(pk=self.q))

        return qs


class StockRecordAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = resources.StockRecordResource
    list_display = ('pk', 'product', 'thumb', 'product_enable', 'product_slug', 'product_partner',
                    'product_categories_to_str', 'price_currency', 'price_excl_tax',
                    'price_retail', 'cost_price', 'num_in_stock', 'num_allocated', 'low_stock_threshold',)
    search_fields = ('product__slug', 'product__title', 'product__pk', )
    list_filter = ('date_created', 'date_updated', 'product__enable', 'product__date_updated', 'product__categories',
                   'product__partner', )
    form = partner_forms.StockRecordForm


class PartnerdAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', )
    search_fields = ('name', 'code',)


admin.site.register(Partner, PartnerdAdmin)
admin.site.register(StockRecord, StockRecordAdmin)
