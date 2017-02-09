from django.conf.urls import url

from oscar.apps.search.app import SearchApplication as BaseSearchApplication


class SearchApplication(BaseSearchApplication):
    def get_urls(self):

        # The form class has to be passed to the __init__ method as that is how
        # Haystack works.  It's slightly different to normal CBVs.
        urlpatterns = [
            url(r'^(?:page/(?P<page>\d+)/)?$', self.search_view.as_view(), name='search'),
            # url(r'^filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)(?:page/(?P<page>\d+)/)?/', self.search_view.as_view(), name='search'),
        ]
        return self.post_process_urls(urlpatterns)

application = SearchApplication()
