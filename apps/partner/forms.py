from django import forms
from models import StockRecord
from dal import autocomplete


class StockRecordForm(forms.ModelForm):
    class Meta:
        model = StockRecord
        widgets = {
            'product': autocomplete.ModelSelect2(url='product-autocomplete'),
            'attributes': autocomplete.ModelSelect2Multiple(url='feature-autocomplete')
        }
        exclude = ('partner', 'partner_sku', )
