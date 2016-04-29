from haystack import indexes

from .models import Product


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    slug = indexes.CharField(model_attr='slug')
    description = indexes.CharField(model_attr='description')
    content_auto = indexes.NgramField(model_attr='title')

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    # def prepare_title_auto(self, obj):
    #     return obj.title.lower()


