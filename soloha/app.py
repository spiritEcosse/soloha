from oscar import app
from django.conf.urls import include, url
from oscar.core.loading import get_class


class Soloha(app.Shop):
    def get_urls(self):
        urlpatterns = super(Soloha, self).get_urls()
        urlpatterns += [
            url(r'', include(self.catalogue_app.urls)),
        ]
        return urlpatterns

application = Soloha()
