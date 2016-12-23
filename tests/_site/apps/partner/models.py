from apps.partner.models import *

# Dummy additional field
offer_name = models.CharField(max_length=128, null=True, blank=True)
offer_name.contribute_to_class(StockRecord, 'offer_name')
