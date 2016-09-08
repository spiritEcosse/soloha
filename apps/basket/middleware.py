from oscar.apps.basket.middleware import BasketMiddleware as CoreBasketMiddleware


class BasketMiddleware(CoreBasketMiddleware):
    def merge_baskets(self, master, slave):
        """
        Merge one basket into another.

        This is its own method to allow it to be overridden
        """
        master.merge(slave, add_quantities=True)
