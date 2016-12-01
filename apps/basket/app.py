from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from soloha.core.application import Application

from apps.basket.views import BasketAddWithAttributesView
from apps.basket.views import BasketView, SavedView, BasketAddView, VoucherAddView, VoucherRemoveView


class BasketApplication(Application):
    name = 'basket'
    summary_view = BasketView
    saved_view = SavedView
    add_view = BasketAddView
    add_voucher_view = VoucherAddView
    remove_voucher_view = VoucherRemoveView
    add_view_with_attributes = BasketAddWithAttributesView

    def get_urls(self):
        urls = [
            url(r'^$', self.summary_view.as_view(), name='summary'),
            url(r'^add/(?P<pk>\d+)/$', self.add_view.as_view(), name='add'),
            url(r'^vouchers/add/$', self.add_voucher_view.as_view(), name='vouchers-add'),
            url(r'^vouchers/(?P<pk>\d+)/remove/$', self.remove_voucher_view.as_view(), name='vouchers-remove'),
            url(r'^saved/$', login_required(self.saved_view.as_view()), name='saved'),
            url(
                r'^add_with_attributes/(?P<pk>\d+)/$', self.add_view_with_attributes.as_view(),
                name='add_with_attributes'
            ),
        ]
        return self.post_process_urls(urls)


application = BasketApplication()
