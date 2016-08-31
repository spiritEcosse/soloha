from django.contrib.sitemaps import Sitemap
from apps.catalogue.models import Product
from apps.catalogue.models import Category
from apps.ex_flatpages.models import FlatPage


class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Product.objects.filter(enable=True)

    def lastmod(self, obj):
        return obj.date_updated


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Category.objects.filter(enable=True)

    def lastmod(self, obj):
        return obj.created


class FlatPageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return FlatPage.objects.filter(enable=True)

    def lastmod(self, obj):
        return obj.created

