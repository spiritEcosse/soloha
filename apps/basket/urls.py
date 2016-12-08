from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from apps.basket.views import BasketAddWithAttributesView
from apps.basket.views import BasketView, SavedView, BasketAddView, VoucherAddView, VoucherRemoveView

urlpatterns = (
    url(r'^$', BasketView.as_view(), name='summary'),
    url(r'^add/(?P<pk>\d+)/$', BasketAddView.as_view(), name='add'),
    url(r'^vouchers/add/$', VoucherAddView.as_view(), name='vouchers-add'),
    url(r'^vouchers/(?P<pk>\d+)/remove/$', VoucherRemoveView.as_view(), name='vouchers-remove'),
    url(r'^saved/$', login_required(SavedView.as_view()), name='saved'),
    url(r'^add_with_attributes/(?P<pk>\d+)/$', BasketAddWithAttributesView.as_view(), name='add_with_attributes'),
)
