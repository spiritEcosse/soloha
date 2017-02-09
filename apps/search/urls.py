from django.conf.urls import url
from haystack.views import search_view_factory

from apps.search.views import FacetedSearchView
from apps.search.forms import SearchForm
from apps.search import facets


def get_sqs():
    """
    Return the SQS required by a the Haystack search view
    """
    return facets.base_sqs()


urlpatterns = [
    url(
        r'^$', search_view_factory(
            view_class=FacetedSearchView, form_class=SearchForm, searchqueryset=get_sqs()
        ), name='search'
    ),
]
