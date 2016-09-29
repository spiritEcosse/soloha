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
        widget=widgets.ForeignKeyWidget(model=Product, field='slug')
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

    def export(self, queryset=None):
        # Todo else not have mind, because this is very slow i.e
        # queryset = self._meta.model.objects.order_by('id', 'cost_price')
        if queryset is not None:
            queryset = queryset.order_by('id', 'cost_price')
        return super(StockRecordResource, self).export(queryset=queryset)
