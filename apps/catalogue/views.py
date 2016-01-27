from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView


class ProductDetailView(CoreProductDetailView):
    def get_object(self, queryset=None):
        # Check if self.object is already set to prevent unnecessary DB calls
        if hasattr(self, 'object'):
            return self.object
        else:

            return super(ProductDetailView, self).get_object(queryset)
