from apps.catalogue import resources
from import_export import fields, widgets as import_export_widgets
from oscar.core.loading import get_model
from django.utils.translation import ugettext_lazy as _
from apps.catalogue import widgets
from apps.catalogue.models import Product, Feature

Partner = get_model('partner', 'Partner')
StockRecord = get_model('partner', 'StockRecord')


class StockRecordResource(resources.ModelResource):
    product = fields.Field(
        attribute='product', column_name='Product slug',
        widget=import_export_widgets.ForeignKeyWidget(model=Product, field='slug')
    )
    attributes = fields.Field(
        attribute='attributes', column_name='Attributes',
        widget=widgets.ManyToManyWidget(model=Feature, field='slug')
    )

    class Meta:
        model = StockRecord
        fields = ('id', 'delete', 'product', 'price_excl_tax', 'price_retail', 'cost_price', 'attributes',
                  'num_in_stock', 'num_allocated', 'low_stock_threshold', )
        export_order = fields
