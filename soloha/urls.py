"""soloha URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse_lazy

from sitemap import ProductSitemap, CategorySitemap, FlatPageSitemap

from apps.catalogue.admin import ProductAutocomplete, FeatureAutocomplete, CategoriesAutocomplete
from apps.partner.admin import PartnerAutocomplete
from apps.ex_flatpages import views
from apps.search.views import FacetedSearchView
from apps.contacts.views import ContactsView
from apps.sitemap.views import SitemapView
from apps.subscribe.views import SubscribeView
from apps.customer.forms import PasswordResetForm, SetPasswordForm

from soloha.core.views.decorators import login_forbidden
from soloha import settings


sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'info_page': FlatPageSitemap
}

urlpatterns = \
    [
        url(r'', include('apps.promotions.urls')),
        url(r'^search/filter/(?P<filter_slug>[\w-]+(/[\w-]+)*)/', FacetedSearchView.as_view()),
        url(r'^search/', FacetedSearchView.as_view()),
        url(r'^contacts/', ContactsView.as_view(), name='contacts'),
        url(r'^ckeditor/', include('ckeditor_uploader.urls')),
        url(r'^filer/', include('filer.urls')),
        url(r'^spirit/product-autocomplete/$', ProductAutocomplete.as_view(), name='product-autocomplete'),
        url(r'^spirit/partner-autocomplete/$', PartnerAutocomplete.as_view(), name='partner-autocomplete'),
        url(r'^spirit/feature-autocomplete/$', FeatureAutocomplete.as_view(), name='feature-autocomplete'),
        url(r'^spirit/categories-autocomplete/$', CategoriesAutocomplete.as_view(), name='categories-autocomplete'),
        url(r'^sitemap/', SitemapView.as_view()),
        url(r'^subscribe/', SubscribeView.as_view()),
        url(r'^pages/(?P<url>[\w-]+)/$', views.flatpage, name='pages'),

        url(r'^catalogue/', include('apps.catalogue.urls')),
        url(r'^basket/', include('apps.basket.urls')),
        url(r'^checkout/', include('apps.checkout.urls')),
        url(r'^accounts/', include('apps.customer.urls')),
        url(r'^search/', include('apps.search.urls')),
        # url(r'^dashboard/', include('apps.dashboard.urls')),
        url(r'^offers/', include('apps.offer.urls')),

        # Password reset - as we're using Django's default view functions,
        # we can't namespace these urls as that prevents
        # the reverse function from working.
        url(r'^password-reset/$', login_forbidden(auth_views.password_reset), {
            'password_reset_form': PasswordResetForm,
            'post_reset_redirect': reverse_lazy('password-reset-done')
        }, name='password-reset'
            ),
        url(r'^password-reset/done/$', login_forbidden(auth_views.password_reset_done),
            name='password-reset-done'),
        url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
            login_forbidden(auth_views.password_reset_confirm), {
                'post_reset_redirect': reverse_lazy('password-reset-complete'),
                'set_password_form': SetPasswordForm,
            },
            name='password-reset-confirm'),
        url(
            r'^password-reset/complete/$', login_forbidden(auth_views.password_reset_complete),
            name='password-reset-complete'
        ),
        url(r'^spirit/', include(admin.site.urls)),
        url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
