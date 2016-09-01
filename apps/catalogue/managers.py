from oscar.apps.catalogue.managers import BrowsableProductManager as BrowsableProductManagerCore
from django.db.models.query import Prefetch


class BrowsableProductManager(BrowsableProductManagerCore):
    """
    Excludes non-canonical products

    Could be deprecated after Oscar 0.7 is released
    """

    def get_queryset(self):
        return super(BrowsableProductManager, self).get_queryset().browsable().\
            select_related('product_class', 'parent__product_class').prefetch_related(
            Prefetch('images'),
            Prefetch('images__original'),
            Prefetch('categories__parent__parent'),
            Prefetch('characteristics'),
            Prefetch('versions'),
        )

