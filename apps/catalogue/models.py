from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractCategory, AbstractProductAttributeValue, \
    AbstractProductAttribute, MissingProductImage as CoreMissingProductImage
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.translation import pgettext_lazy
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.html import strip_entities
from easy_thumbnails.files import get_thumbnailer
import logging
from soloha.settings import IMAGE_NOT_FOUND
from oscar.apps.partner.strategy import Selector
from django.contrib.postgres.fields import ArrayField
from django.core import serializers
from easy_thumbnails.exceptions import (
    InvalidImageFormatError, EasyThumbnailsError)
from django.utils.text import slugify
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
    sort = models.IntegerField(blank=True, null=True, default=0)
    node_order_by = ['sort']
    icon = models.ImageField(_('Icon'), upload_to='categories', blank=True, null=True, max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    image_banner = models.ImageField(_('Image banner'), upload_to='categories', blank=True, null=True, max_length=255)
    link_banner = models.URLField(_('Link banner'), blank=True, null=True, max_length=255)
    objects = CategoryEnable()
    url = models.URLField(_('Full slug'), max_length=1000, editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Create a url from the url of the parent of the current slug
        Args:
            *args:
            **kwargs:

        Returns:

        """
        if not self.slug:
            self.slug = slugify(self.name)

        try:
            Category.objects.get(slug=self.slug)
        except ObjectDoesNotExist:
            self.slug = self.slug
        else:
            raise ValueError('This slug "{}" the exists already. (Name "{}")'.format(self.slug, self.name))

        self.url = self.slug

        if self.parent():
            self.url = '{}/{}'.format(self.parent().url, self.url)
        super(AbstractCategory, self).save(*args, **kwargs)

    def get_values(self):
        return {
            'name': self.name,
            'icon': self.get_icon(),
            'absolute_url': self.get_absolute_url(),
            'slug': self.slug,
            'image_banner': self.get_image_banner(),
            'link_banner': self.link_banner,
        }

    def get_image_banner(self):
        image_banner = ''

        if self.image_banner:
            options = {'size': (544, 212), 'crop': True}
            image_banner = get_thumbnailer(self.image_banner).get_thumbnail(options).url
        return image_banner

    def get_absolute_url(self):
        cache_key = 'CATEGORY_URL_%s' % self.pk
        url = cache.get(cache_key)

        if not url:
            url = reverse('category', kwargs={'category_slug': self.url})
            cache.set(cache_key, url)
        return url

    @classmethod
    def get_annotated_list_qs_depth(cls, parent=None, max_depth=None):
        """
        Gets an annotated list from a tree branch, change queryset

        :param parent:

            The node whose descendants will be annotated. The node itself
            will be included in the list. If not given, the entire tree
            will be annotated.

        :param max_depth:

            Optionally limit to specified depth

        :sort_order

            Sort order queryset.

        """

        result, info = [], {}
        start_depth, prev_depth = (None, None)
        qs = cls.get_tree(parent)
        if max_depth:
            qs = qs.filter(depth__lte=max_depth)
        return cls.get_annotated_list_qs(qs)

    @classmethod
    def dump_bulk_depth(cls, parent=None, keep_ids=True, max_depth=3):
        """
        Dumps a tree branch to a python type structure.

        Args:
            parent: by default None (if you set the Parent to the object category then we obtain a tree search)
            keep_ids: by default True (if True add id category in data)
            max_depth: by default 3 (max depth in category tree) (if max_depth = 0 return all tree)

        Returns:
        [{'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
                {'data': category.get_values()},
                {'data': category.get_values(), 'children':[
                    {'data': category.get_values()},
                ]},
                {'data': category.get_values()},
            ]},
            {'data': category.get_values()},
            {'data': category.get_values(), 'children':[
                {'data': category.get_values()},
            ]},
        ]
        """
        # Because of fix_tree, this method assumes that the depth
        # and numchild properties in the nodes can be incorrect,
        # so no helper methods are used
        data = cls.get_annotated_list_qs_depth(max_depth=max_depth)
        ret, lnk = [], {}

        for pyobj, info in data:
            # django's serializer stores the attributes in 'fields'
            path = pyobj.path
            depth = int(len(path) / cls.steplen)
            # this will be useless in load_bulk

            newobj = {'data': pyobj.get_values()}

            if keep_ids:
                newobj['id'] = pyobj.pk

            if (not parent and depth == 1) or \
                    (parent and len(path) == len(parent.path)):
                ret.append(newobj)
            else:
                parentpath = cls._get_basepath(path, depth - 1)
                parentobj = lnk[parentpath]
                if 'children' not in parentobj:
                    parentobj['children'] = []
                parentobj['children'].append(newobj)
            lnk[path] = newobj
        return ret

    def get_icon(self):
        icon = ''

        if self.icon:
            options = {'size': (50, 31), 'crop': True}
            icon = get_thumbnailer(self.icon).get_thumbnail(options).url
        return icon

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
            category_slug = self.categories.get().category.url
        except MultipleObjectsReturned:
            kw['category_slug'] = self.categories.first().category.url
        except ObjectDoesNotExist:
            logger.error('Product object "{}" does not have categories'.format(self))
        else:
            kw['category_slug'] = category_slug

        return reverse('detail', kwargs=kw)

    def get_values(self):
        values = dict()
        values['title'] = strip_entities(self.title)

        if self.categories.first():
            values['absolute_url'] = self.categories.first().category.url
        else:
            values['absolute_url'] = self.slug

        # selector = Selector()
        # strategy = selector.strategy()
        # info = strategy.fetch_for_product(self)
        # values['price'] = str(info.price.incl_tax)
        options = {'size': (220, 165), 'crop': True}

        image = getattr(self.primary_image(), 'original', IMAGE_NOT_FOUND)

        try:
            values['image'] = get_thumbnailer(image).get_thumbnail(options).url
        except InvalidImageFormatError:
            values['image'] = get_thumbnailer(IMAGE_NOT_FOUND).get_thumbnail(options).url
        return values



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
