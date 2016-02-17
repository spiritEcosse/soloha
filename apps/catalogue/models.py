from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractCategory, AbstractProductAttributeValue, \
    AbstractProductAttribute, MissingProductImage as CoreMissingProductImage
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import pgettext_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import strip_entities
from easy_thumbnails.files import get_thumbnailer
import logging
from soloha.settings import IMAGE_NOT_FOUND
from oscar.apps.partner.strategy import Selector
from django.contrib.postgres.fields import ArrayField

logger = logging.getLogger(__name__)


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
            url = reverse('category', kwargs={'category_slug': self.full_slug})
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
        kw = {'slug': self.slug}

        try:
            category_slug = self.categories.get().full_slug
        except ObjectDoesNotExist:
            pass
        else:
            kw['category_slug'] = category_slug

        return reverse('detail', kwargs=kw)

    def get_values(self):
        values = dict()
        values['title'] = strip_entities(self.title)
        values['absolute_url'] = self.get_absolute_url()
        selector = Selector()
        strategy = selector.strategy()
        info = strategy.fetch_for_product(self)
        values['price'] = str(info.price.incl_tax)
        options = {'size': (220, 165), 'crop': True}
        values['image'] = get_thumbnailer(getattr(self.primary_image(), 'original', IMAGE_NOT_FOUND)).get_thumbnail(options).url
        return values

    def primary_image(self):
        """
        Returns the primary image for a product. Usually used when one can
        only display one product image, e.g. in a list of products.
        """
        images = self.images.all()
        ordering = self.images.model.Meta.ordering
        if not ordering or ordering[0] != 'display_order':
            # Only apply order_by() if a custom model doesn't use default
            # ordering. Applying order_by() busts the prefetch cache of
            # the ProductManager
            images = images.order_by('display_order')
        try:
            return images[0]
        except IndexError:
            # We return a dict with fields that mirror the key properties of
            # the ProductImage class so this missing image can be used
            # interchangeably in templates.  Strategy pattern ftw!
            return {
                'original': IMAGE_NOT_FOUND,
                'caption': '',
                'is_missing': True
            }


# class MissingProductImage(CoreMissingProductImage):
#     def __init__(self, name=None):
#         super(MissingProductImage, self).__init__()
#         print self.name


class ProductAttributeValue(AbstractProductAttributeValue):
    pass

# class GroupFilter(models.Model):
#     name = models.CharField(_('Name filter'), max_length=128)
#
#     def __str__(self):
#         return self.name
#
#     class Meta:
#         abstract = True
#         app_label = 'catalogue'
#         verbose_name = _('Filter group')
#         verbose_name_plural = _('Filter groups')
#

# class ProductAttribute(AbstractProductAttribute):
#     pos_option = models.BooleanField(verbose_name=_('This is option'), default=False, db_index=True)
#     pos_attribute = models.BooleanField(verbose_name=_('This is attribute'), default=False, db_index=True)
    # pos_filter = models.BooleanField(verbose_name=_('This is filter'), default=False, db_index=True)
    # pos_characteristic = models.BooleanField(verbose_name=_('This is characteristic'), default=False, db_index=True)


from oscar.apps.catalogue.models import *
