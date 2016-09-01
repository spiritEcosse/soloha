from oscar.apps.basket.abstract_models import *  # noqa


class Basket(AbstractBasket):
    def all_lines(self):
        """
        Return a cached set of basket lines.

        This is important for offers as they alter the line models and you
        don't want to reload them from the DB as that information would be
        lost.
        """
        if self.id is None:
            return self.lines.none()
        if self._lines is None:
            self._lines = (
                self.lines
                    .select_related('product', 'product__product_class', 'stockrecord')
                    .prefetch_related('attributes', 'product__images', 'product__categories__parent__parent',
                                      'product__stockrecords'))
        return self._lines

from oscar.apps.basket.models import *  # noqa
