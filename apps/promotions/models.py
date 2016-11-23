from oscar.apps.promotions.models import *
from apps.catalogue.models import Product
from django.db.models import Max, Min


def get_queryset(self):
    qs = Product.objects.browse()

    if self.method == self.BESTSELLING:
        return qs.order_by('-stats__score')

    return qs.order_by('-date_created')


AutomaticProductList.get_queryset = get_queryset
PagePromotion._meta.get_field('display_order').db_index = True
