

class Filter(object):
    lookup_parent = '__parent'

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

    def filter_product_stockrecord(self, additional={}):
        lookup_feature = 'product'

        if self.product.is_parent:
            lookup_feature += self.lookup_parent

        filter_kw = {lookup_feature: self.product}
        filter_kw.update(additional)
        return filter_kw

