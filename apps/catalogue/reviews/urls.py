from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.catalogue.reviews.views import ProductReviewDetail, CreateProductReview, AddVoteView, ProductReviewList

urlpatterns = (
    url(r'^(?P<pk>\d+)/$', ProductReviewDetail.as_view(), name='reviews-detail'),
    url(r'^add/$', CreateProductReview.as_view(), name='reviews-add'),
    url(r'^(?P<pk>\d+)/vote/$', login_required(AddVoteView.as_view()), name='reviews-vote'),
    url(r'^$', ProductReviewList.as_view(), name='reviews-list'),
)
