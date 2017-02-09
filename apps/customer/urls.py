from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views import generic

from apps.customer.views import AccountSummaryView, OrderHistoryView, OrderDetailView, AnonymousOrderDetailView, \
    OrderLineView, AddressListView, AddressCreateView, AddressUpdateView, AddressDeleteView, AddressChangeStatusView, \
    EmailHistoryView, EmailDetailView, AccountAuthView, LogoutView, AccountRegistrationView, ProfileView, \
    ProfileUpdateView, ProfileDeleteView, ChangePasswordView
from apps.customer.notifications.views import InboxView, ArchiveView, UpdateView, DetailView
from apps.customer.alerts.views import ProductAlertListView, ProductAlertCreateView, ProductAlertConfirmView, \
    ProductAlertCancelView
from apps.customer.wishlists.views import WishListAddProduct, WishListListView, WishListDetailView, \
    WishListCreateView, WishListUpdateView, WishListDeleteView, WishListRemoveProduct, \
    WishListMoveProductToAnotherWishList


urlpatterns = (
    # Login, logout and register doesn't require login
    url(r'^login/$', AccountAuthView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', AccountRegistrationView.as_view(), name='register'),
    url(r'^$', login_required(AccountSummaryView.as_view()), name='summary'),
    url(r'^change-password/$', login_required(ChangePasswordView.as_view()), name='change-password'),

    # Profile
    url(r'^profile/$', login_required(ProfileView.as_view()), name='profile-view'),
    url(r'^profile/edit/$', login_required(ProfileUpdateView.as_view()), name='profile-update'),
    url(r'^profile/delete/$', login_required(ProfileDeleteView.as_view()), name='profile-delete'),

    # Order history
    url(r'^orders/$', login_required(OrderHistoryView.as_view()), name='order-list'),
    url(r'^order-status/(?P<order_number>[\w-]*)/(?P<hash>\w+)/$', AnonymousOrderDetailView.as_view(), name='anon-order'),
    url(r'^orders/(?P<order_number>[\w-]*)/$', login_required(OrderDetailView.as_view()), name='order'),
    url(
        r'^orders/(?P<order_number>[\w-]*)/(?P<line_id>\d+)$', login_required(OrderLineView.as_view()),
        name='order-line'
    ),

    # Address book
    url(r'^addresses/$', login_required(AddressListView.as_view()), name='address-list'),
    url(r'^addresses/add/$', login_required(AddressCreateView.as_view()), name='address-create'),
    url(r'^addresses/(?P<pk>\d+)/$', login_required(AddressUpdateView.as_view()), name='address-detail'),
    url(
        r'^addresses/(?P<pk>\d+)/delete/$',
        login_required(AddressDeleteView.as_view()), name='address-delete'
    ),
    url(
        r'^addresses/(?P<pk>\d+)/(?P<action>default_for_(billing|shipping))/$',
        login_required(AddressChangeStatusView.as_view()), name='address-change-status'
    ),

    # Email history
    url(r'^emails/$', login_required(EmailHistoryView.as_view()), name='email-list'),
    url(r'^emails/(?P<email_id>\d+)/$', login_required(EmailDetailView.as_view()), name='email-detail'),

    # Notifications
    # Redirect to notification inbox
    url(r'^notifications/$', generic.RedirectView.as_view(url='/accounts/notifications/inbox/')),
    url(
        r'^notifications/inbox/$', login_required(InboxView.as_view()),
        name='notifications-inbox'
    ),
    url(
        r'^notifications/archive/$', login_required(ArchiveView.as_view()),
        name='notifications-archive'
    ),
    url(
        r'^notifications/update/$', login_required(UpdateView.as_view()),
        name='notifications-update'
    ),
    url(
        r'^notifications/(?P<pk>\d+)/$', login_required(DetailView.as_view()),
        name='notifications-detail'
    ),

    # Alerts
    # Alerts can be setup by anonymous users: some views do not
    # require login
    url(r'^alerts/$', login_required(ProductAlertListView.as_view()), name='alerts-list'),
    url(r'^alerts/create/(?P<pk>\d+)/$', ProductAlertCreateView.as_view(), name='alert-create'),
    url(r'^alerts/confirm/(?P<key>[a-z0-9]+)/$', ProductAlertConfirmView.as_view(), name='alerts-confirm'),
    url(
        r'^alerts/cancel/key/(?P<key>[a-z0-9]+)/$', ProductAlertCancelView.as_view(),
        name='alerts-cancel-by-key'
    ),
    url(
        r'^alerts/cancel/(?P<pk>[a-z0-9]+)/$', login_required(ProductAlertCancelView.as_view()),
        name='alerts-cancel-by-pk'
    ),

    # Wishlists
    url(r'wishlists/$', login_required(WishListListView.as_view()), name='wishlists-list'),
    url(
        r'wishlists/add/(?P<product_pk>\d+)/$', login_required(WishListAddProduct.as_view()),
        name='wishlists-add-product'
    ),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/add/(?P<product_pk>\d+)/',
        login_required(WishListAddProduct.as_view()),
        name='wishlists-add-product'
    ),
    url(r'wishlists/create/$', login_required(WishListCreateView.as_view()), name='wishlists-create'),
    url(
        r'wishlists/create/with-product/(?P<product_pk>\d+)/$',
        login_required(WishListCreateView.as_view()),
        name='wishlists-create-with-product'
    ),
    # Wishlists can be publicly shared, no login required
    url(r'wishlists/(?P<key>[a-z0-9]+)/$', WishListDetailView.as_view(), name='wishlists-detail'),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/update/$', login_required(WishListUpdateView.as_view()),
        name='wishlists-update'
    ),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/delete/$', login_required(WishListDeleteView.as_view()),
        name='wishlists-delete'
    ),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/lines/(?P<line_pk>\d+)/delete/',
        login_required(WishListRemoveProduct.as_view()),
        name='wishlists-remove-product'
    ),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/products/(?P<product_pk>\d+)/delete/',
        login_required(WishListRemoveProduct.as_view()),
        name='wishlists-remove-product'
    ),
    url(
        r'wishlists/(?P<key>[a-z0-9]+)/lines/(?P<line_pk>\d+)/move-to/(?P<to_key>[a-z0-9]+)/$',
        login_required(WishListMoveProductToAnotherWishList.as_view()),
        name='wishlists-move-product-to-another'
    )
)
