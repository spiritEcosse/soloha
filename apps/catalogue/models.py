from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractCategory
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.core.urlresolvers import reverse


class CategoryEnable(models.Manager):
    def get_queryset(self):
        return super(CategoryEnable, self).get_queryset().filter(enable=1)


class Category(AbstractCategory):
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    sort = models.IntegerField(blank=True, null=True)
    objects = CategoryEnable()

    def get_absolute_url(self):
        cache_key = 'CATEGORY_URL_%s' % self.pk
        url = cache.get(cache_key)

        if not url:
            url = reverse('catalogue:category', kwargs={'category_slug': self.full_slug})
            cache.set(cache_key, url)
        return url

    def parent(self):
        return self.get_parent()
    parent.short_description = _('Get parent')


class Product(AbstractProduct):
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)

    def get_absolute_url(self):
        """
        Return a product's absolute url
        """
        return reverse('catalogue:detail', kwargs={'product_slug': self.slug})

from oscar.apps.catalogue.models import *
