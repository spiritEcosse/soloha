from django.conf.urls import url

from apps.checkout.views import IndexView, UserAddressUpdateView, UserAddressDeleteView, ShippingAddressView, \
    ShippingMethodView, PaymentDetailsView, PaymentMethodView, ThankYouView

urlpatterns = (
    url(r'^$', IndexView.as_view(), name='index'),

    # Shipping/user address views
    url(r'shipping-address/$', ShippingAddressView.as_view(), name='shipping-address'),
    url(r'user-address/edit/(?P<pk>\d+)/$', UserAddressUpdateView.as_view(), name='user-address-update'),
    url(r'user-address/delete/(?P<pk>\d+)/$', UserAddressDeleteView.as_view(), name='user-address-delete'),

    # Shipping method views
    url(r'shipping-method/$', ShippingMethodView.as_view(), name='shipping-method'),

    # Payment views
    url(r'payment-method/$', PaymentMethodView.as_view(), name='payment-method'),
    url(r'payment-details/$', PaymentDetailsView.as_view(), name='payment-details'),

    # Preview and thank_you
    url(r'preview/$', PaymentDetailsView.as_view(preview=True), name='preview'),
    url(r'thank-you/$', ThankYouView.as_view(), name='thank-you'),
)
