from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views import generic

from soloha.core.application import Application

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


class CustomerApplication(Application):
    name = 'customer'
    summary_view = AccountSummaryView
    order_history_view = OrderHistoryView
    order_detail_view = OrderDetailView
    anon_order_detail_view = AnonymousOrderDetailView
    order_line_view = OrderLineView

    address_list_view = AddressListView
    address_create_view = AddressCreateView
    address_update_view = AddressUpdateView
    address_delete_view = AddressDeleteView
    address_change_status_view = AddressChangeStatusView

    email_list_view = EmailHistoryView
    email_detail_view = EmailDetailView
    login_view = AccountAuthView
    logout_view = LogoutView
    register_view = AccountRegistrationView
    profile_view = ProfileView
    profile_update_view = ProfileUpdateView
    profile_delete_view = ProfileDeleteView
    change_password_view = ChangePasswordView

    notification_inbox_view = InboxView
    notification_archive_view = ArchiveView
    notification_update_view = UpdateView
    notification_detail_view = DetailView

    alert_list_view = ProductAlertListView
    alert_create_view = ProductAlertCreateView
    alert_confirm_view = ProductAlertConfirmView
    alert_cancel_view = ProductAlertCancelView

    wishlists_add_product_view = WishListAddProduct
    wishlists_list_view = WishListListView
    wishlists_detail_view = WishListDetailView
    wishlists_create_view = WishListCreateView
    wishlists_create_with_product_view = WishListCreateView
    wishlists_update_view = WishListUpdateView
    wishlists_delete_view = WishListDeleteView
    wishlists_remove_product_view = WishListRemoveProduct
    wishlists_move_product_to_another_view = WishListMoveProductToAnotherWishList

    def get_urls(self):
        urls = [
            # Login, logout and register doesn't require login
            url(r'^login/$', self.login_view.as_view(), name='login'),
            url(r'^logout/$', self.logout_view.as_view(), name='logout'),
            url(r'^register/$', self.register_view.as_view(), name='register'),
            url(r'^$', login_required(self.summary_view.as_view()), name='summary'),
            url(r'^change-password/$', login_required(self.change_password_view.as_view()), name='change-password'),

            # Profile
            url(r'^profile/$', login_required(self.profile_view.as_view()), name='profile-view'),
            url(r'^profile/edit/$', login_required(self.profile_update_view.as_view()), name='profile-update'),
            url(r'^profile/delete/$', login_required(self.profile_delete_view.as_view()), name='profile-delete'),

            # Order history
            url(r'^orders/$', login_required(self.order_history_view.as_view()), name='order-list'),
            url(r'^order-status/(?P<order_number>[\w-]*)/(?P<hash>\w+)/$',
                self.anon_order_detail_view.as_view(), name='anon-order'),
            url(r'^orders/(?P<order_number>[\w-]*)/$', login_required(self.order_detail_view.as_view()), name='order'),
            url(
                r'^orders/(?P<order_number>[\w-]*)/(?P<line_id>\d+)$', login_required(self.order_line_view.as_view()),
                name='order-line'
            ),

            # Address book
            url(r'^addresses/$', login_required(self.address_list_view.as_view()), name='address-list'),
            url(r'^addresses/add/$', login_required(self.address_create_view.as_view()), name='address-create'),
            url(r'^addresses/(?P<pk>\d+)/$', login_required(self.address_update_view.as_view()), name='address-detail'),
            url(
                r'^addresses/(?P<pk>\d+)/delete/$',
                login_required(self.address_delete_view.as_view()), name='address-delete'
            ),
            url(
                r'^addresses/(?P<pk>\d+)/(?P<action>default_for_(billing|shipping))/$',
                login_required(self.address_change_status_view.as_view()), name='address-change-status'
            ),

            # Email history
            url(r'^emails/$', login_required(self.email_list_view.as_view()), name='email-list'),
            url(r'^emails/(?P<email_id>\d+)/$', login_required(self.email_detail_view.as_view()), name='email-detail'),

            # Notifications
            # Redirect to notification inbox
            url(r'^notifications/$', generic.RedirectView.as_view(url='/accounts/notifications/inbox/')),
            url(
                r'^notifications/inbox/$', login_required(self.notification_inbox_view.as_view()),
                name='notifications-inbox'
            ),
            url(
                r'^notifications/archive/$', login_required(self.notification_archive_view.as_view()),
                name='notifications-archive'
            ),
            url(
                r'^notifications/update/$', login_required(self.notification_update_view.as_view()),
                name='notifications-update'
            ),
            url(
                r'^notifications/(?P<pk>\d+)/$', login_required(self.notification_detail_view.as_view()),
                name='notifications-detail'
            ),

            # Alerts
            # Alerts can be setup by anonymous users: some views do not
            # require login
            url(r'^alerts/$', login_required(self.alert_list_view.as_view()), name='alerts-list'),
            url(r'^alerts/create/(?P<pk>\d+)/$', self.alert_create_view.as_view(), name='alert-create'),
            url(r'^alerts/confirm/(?P<key>[a-z0-9]+)/$', self.alert_confirm_view.as_view(), name='alerts-confirm'),
            url(
                r'^alerts/cancel/key/(?P<key>[a-z0-9]+)/$', self.alert_cancel_view.as_view(),
                name='alerts-cancel-by-key'
            ),
            url(
                r'^alerts/cancel/(?P<pk>[a-z0-9]+)/$', login_required(self.alert_cancel_view.as_view()),
                name='alerts-cancel-by-pk'
            ),

            # Wishlists
            url(r'wishlists/$', login_required(self.wishlists_list_view.as_view()), name='wishlists-list'),
            url(
                r'wishlists/add/(?P<product_pk>\d+)/$', login_required(self.wishlists_add_product_view.as_view()),
                name='wishlists-add-product'
            ),
            url(
                r'wishlists/(?P<key>[a-z0-9]+)/add/(?P<product_pk>\d+)/',
                login_required(self.wishlists_add_product_view.as_view()),
                name='wishlists-add-product'
            ),
            url(r'wishlists/create/$', login_required(self.wishlists_create_view.as_view()), name='wishlists-create'),
            url(
                r'wishlists/create/with-product/(?P<product_pk>\d+)/$', login_required(self.wishlists_create_view.as_view()),
                name='wishlists-create-with-product'
            ),
            # Wishlists can be publicly shared, no login required
            url(r'wishlists/(?P<key>[a-z0-9]+)/$', self.wishlists_detail_view.as_view(), name='wishlists-detail'),
            url(r'wishlists/(?P<key>[a-z0-9]+)/update/$', login_required(self.wishlists_update_view.as_view()),
                name='wishlists-update'),
            url(r'wishlists/(?P<key>[a-z0-9]+)/delete/$', login_required(self.wishlists_delete_view.as_view()),
                name='wishlists-delete'),
            url(
                r'wishlists/(?P<key>[a-z0-9]+)/lines/(?P<line_pk>\d+)/delete/',
                login_required(self.wishlists_remove_product_view.as_view()),
                name='wishlists-remove-product'
            ),
            url(
                r'wishlists/(?P<key>[a-z0-9]+)/products/(?P<product_pk>\d+)/delete/',
                login_required(self.wishlists_remove_product_view.as_view()),
                name='wishlists-remove-product'
            ),
            url(
                r'wishlists/(?P<key>[a-z0-9]+)/lines/(?P<line_pk>\d+)/move-to/(?P<to_key>[a-z0-9]+)/$',
                login_required(self.wishlists_move_product_to_another_view.as_view()),
                name='wishlists-move-product-to-another'
            )
        ]

        return self.post_process_urls(urls)


application = CustomerApplication()
