from django.conf.urls import url
from oscar.apps.catalogue.app import CatalogueApplication as CoreCatalogueApplication


class Catalogue(CoreCatalogueApplication):
    def get_urls(self):
        urlpatterns = [
            url(r'^catalogue/$', self.catalogue_view.as_view(), name='index'),
            url(r'^(?P<category_slug>[\w-]+(/[\w-]+)*)/$', self.category_view.as_view(), name='category'),
            url(r'^(?P<product_slug>[\w-]+)/$', self.detail_view.as_view(), name='detail'),
        ]
        urlpatterns += super(Catalogue, self).get_urls()
        return urlpatterns

application = Catalogue()
