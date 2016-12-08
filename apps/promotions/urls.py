from django.conf.urls import url

from apps.promotions.models import PagePromotion, KeywordPromotion
from apps.promotions.views import HomeView, RecordClickView


urlpatterns = (
    url(
        r'page-redirect/(?P<page_promotion_id>\d+)/$',
        RecordClickView.as_view(model=PagePromotion),
        name='page-click'
    ),
    url(
        r'keyword-redirect/(?P<keyword_promotion_id>\d+)/$',
        RecordClickView.as_view(model=KeywordPromotion),
        name='keyword-click'
    ),
    url(r'^$', HomeView.as_view(), name='home'),
)
