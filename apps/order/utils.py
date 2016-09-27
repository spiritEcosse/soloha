from oscar.core.loading import get_model
from oscar.core.loading import get_class
from oscar.apps.order.utils import OrderCreator as CoreOrderCreator


Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
OrderDiscount = get_model('order', 'OrderDiscount')
order_placed = get_class('order.signals', 'order_placed')


class OrderCreator(CoreOrderCreator):
    def create_line_attributes(self, order, order_line, basket_line):
        """
        Creates the batch line attributes.
        """
        for attr in basket_line.attributes.all():
            line_attributes = order_line.attributes.create(feature=attr.feature)

            if getattr(attr, 'product_images', None):
                line_attributes.product_images.add(*attr.product_images.all())
