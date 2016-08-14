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
from soloha.app import application
from django.conf.urls.static import static
from soloha import settings
from django.contrib.sitemaps.views import sitemap
from sitemap import ProductSitemap, CategorySitemap, InfoPageSitemap


sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'info_page': InfoPageSitemap
}


urlpatterns = [
                  url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
                  url(r'^spirit/', include(admin.site.urls)),
                  url(r'', include(application.urls)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
