from apps.catalogue import resources
from import_export import fields, widgets as import_export_widgets
from import_export.admin import ImportExportMixin, ImportExportActionModelAdmin
from oscar.apps.partner.admin import *  # noqa

Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')
Product = get_model('catalogue', 'Product')


class StockRecordResource(resources.ModelResource):
    product = fields.Field(column_name='product', attribute='product', widget=import_export_widgets.ForeignKeyWidget(
        model=Product, field='slug'
    ))
    partner = fields.Field(column_name='partner', attribute='partner', widget=import_export_widgets.ForeignKeyWidget(
        model=Partner, field='code'
    ))
    delete = fields.Field(widget=import_export_widgets.BooleanWidget())

    class Meta:
        model = StockRecord
        fields = ('id', 'delete', 'product', 'partner', 'partner_sku', 'price_excl_tax', 'price_retail', 'cost_price',
                  'num_in_stock', 'num_allocated', 'low_stock_threshold', )
        export_order = fields

    # ToDo @igor: user cannot delete if has permission
    def for_delete(self, row, instance):
        return self.fields['delete'].clean(row)


class StockRecordAdmin(ImportExportMixin, ImportExportActionModelAdmin):
    resource_class = StockRecordResource
    list_display = ('pk', 'product', 'thumb', 'enable_product', 'partner', 'price_currency', 'price_excl_tax',
                    'price_retail', 'cost_price', 'num_in_stock', 'num_allocated', 'low_stock_threshold',
                    'product_categories_to_str', )
    search_fields = ('product__slug', 'product__title', 'product__pk', )
    list_filter = ('date_created', 'date_updated', 'product__enable', 'product__date_updated', 'product__categories',
                   'partner', )


class PartnerdAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'code', )
    search_fields = ('name', 'code',)


admin.site.unregister(Partner)
admin.site.register(Partner, PartnerdAdmin)
admin.site.unregister(StockRecord)
admin.site.register(StockRecord, StockRecordAdmin)
