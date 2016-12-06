from django.conf.urls import url
from apps.offer.views import OfferDetailView, OfferListView


urlpatterns = \
    [
        url(r'^$', OfferListView.as_view(), name='list'),
        url(r'^(?P<slug>[\w-]+)/$', OfferDetailView.as_view(), name='detail'),
    ]
