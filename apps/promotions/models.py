from oscar.apps.promotions.models import *
from apps.catalogue.models import Product


def get_queryset(self):
    qs = Product.objects.browse().select_related('stats')

    if self.method == self.BESTSELLING:
        return qs.order_by('-stats__score')

    return qs.order_by('-date_created')


AutomaticProductList.get_queryset = get_queryset
