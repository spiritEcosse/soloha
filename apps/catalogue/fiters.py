

class Filter(object):
    def __init__(self, product):
        self.product = product

    def filter_feature_parent(self, additional={}):
        filter_product_feature = {}
        lookup_product_feature = 'product'
        product = self.product

        if self.product.is_child:
            product = self.product.parent

        filter_product_feature[lookup_product_feature] = product
        filter_product_feature.update(**additional)
        return filter_product_feature
