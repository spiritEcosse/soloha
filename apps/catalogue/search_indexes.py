from django.utils import timezone
from haystack import indexes

from .models import Product
from oscar.apps.partner.strategy import Selector


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.CharField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    slug = indexes.CharField(model_attr='slug')
    description = indexes.CharField(model_attr='description')

    # rendered = indexes.CharField(use_template=True, indexed=False)

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def get_price(self):
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(self.object)
        price = info.price.incl_tax
        return price
