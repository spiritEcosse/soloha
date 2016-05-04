from haystack import indexes

from oscar.core.loading import get_model
Product = get_model('catalogue', 'product')


# from .models import Product


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    # id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    slug = indexes.CharField(model_attr='slug')
    # description = indexes.CharField(model_attr='description')
    title_ngrams = indexes.EdgeNgramField(model_attr='title')
    slug_ngrams = indexes.EdgeNgramField(model_attr='slug')
    id_ngrams = indexes.EdgeNgramField(model_attr='id')

    # solr needs suggestion
    suggestions = indexes.FacetCharField()

    def get_model(self):
        return Product

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

    # needed for solr
    def prepare(self, obj):
        prepared_data = super(ProductIndex, self).prepare(obj)
        prepared_data['suggestions'] = prepared_data['text']
        return prepared_data


    # def prepare_title_auto(self, obj):
    #     return obj.title.lower()


