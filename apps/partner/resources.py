from apps.catalogue import resources
from import_export import fields, widgets as import_export_widgets
from oscar.core.loading import get_model
from django.utils.translation import ugettext_lazy as _

Product = get_model('catalogue', 'Product')
ProductVersion = get_model('catalogue', 'ProductVersion')
Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')


class StockRecordResource(resources.ModelResource):
    product = fields.Field(
        attribute='product_version__product', column_name=_('Product title (will not change the product)'),
        widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    product_version = fields.Field(
        attribute='product_version', column_name=_('Version of product'),
        widget=import_export_widgets.ForeignKeyWidget(model=ProductVersion)
    )

    class Meta:
        model = StockRecord
        fields = ('id', 'delete', 'product_version', 'product', 'price_excl_tax', 'price_retail', 'cost_price',
                  'num_in_stock', 'num_allocated', 'low_stock_threshold', )
        export_order = fields
