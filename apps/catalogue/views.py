from oscar.apps.catalogue.views import ProductCategoryView as CoreProductCategoryView
from oscar.apps.catalogue.views import ProductDetailView as CoreProductDetailView
from apps.catalogue.models import Product, ProductAttribute, AttributeOptionGroup, AttributeOption, ProductAttributeValue
from django.db.models.query import Prefetch
from oscar.apps.partner.strategy import Selector
from django.utils.translation import ugettext_lazy as _


class ProductCategoryView(CoreProductCategoryView):
    template_name = 'catalogue/soloha_category.html'


class ProductDetailView(CoreProductDetailView):
    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(self.object)

        if info.availability.is_available_to_buy:
            context['price'] = info.price.incl_tax
            context['currency'] = info.price.currency
        else:
            context['product_not_availability'] = _('Product is not available.')
        return context
