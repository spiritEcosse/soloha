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
from django.core import serializers

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
    icon = models.ImageField(_('Icon'), upload_to='categories', blank=True, null=True, max_length=255)

    def get_absolute_url(self):
        cache_key = 'CATEGORY_URL_%s' % self.pk
        url = cache.get(cache_key)

        if not url:
            url = reverse('category', kwargs={'category_slug': self.full_slug})
            cache.set(cache_key, url)
        return url

    @classmethod
    def dump_bulk_depth(cls, parent=None, keep_ids=True):
        """Dumps a tree branch to a python data structure."""

        # Because of fix_tree, this method assumes that the depth
        # and numchild properties in the nodes can be incorrect,
        # so no helper methods are used
        qset = cls._get_serializable_model().get_annotated_list(max_depth=2)
        if parent:
            qset = qset.filter(path__startswith=parent.path)
        ret, lnk = [], {}
        for pyobj in serializers.serialize('python', qset):
            # django's serializer stores the attributes in 'fields'
            fields = pyobj['fields']
            path = fields['path']
            depth = int(len(path) / cls.steplen)
            # this will be useless in load_bulk
            del fields['depth']
            del fields['path']
            del fields['numchild']
            if 'id' in fields:
                # this happens immediately after a load_bulk
                del fields['id']

            newobj = {'data': fields}
            if keep_ids:
                newobj['id'] = pyobj['pk']

            if (not parent and depth == 1) or\
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

    @classmethod
    def dump_obj(cls):
        """Recursively obtaining categories."""
        res_categories = []
        categories = Category.get_root_nodes().filter(enable=True).order_by('sort')
        options = {'size': (50, 31), 'crop': True}

        for obj in categories:
            if obj.has_children():
                setattr(obj, 'children', obj.get_rec_cat())

            icon = obj.get_icon()
            res_categories.append({
                'name': obj.name,
                'icon': get_thumbnailer(icon).get_thumbnail(options).url,
                'children': obj.children
            })

    def get_rec_cat(self):
        children = []

        for category in self.get_children():
            if category.has_children():
                setattr(category, 'children', category.get_rec_cat())

            children.append({
                'name': category.name,
                'absolute_url': category.get_absolute_url(),
                'children': category.children
            })

        return children

    def get_icon(self):
        return self.icon or IMAGE_NOT_FOUND

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
