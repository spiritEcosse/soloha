from oscar.apps.order.models import *  # noqa
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from oscar.core.loading import get_model
from oscar.models.fields import AutoSlugField

Product = get_model('catalogue', 'Product')


class QuickOrder(models.Model):
    name = models.CharField(verbose_name=_('Name client'), max_length=30)
    phone_number = models.CharField(
        verbose_name=_('Phone number client'), max_length=19)
    email = models.EmailField(verbose_name=_('Email client'), max_length=200, blank=True)
    comment = models.CharField(verbose_name=_('Comment client'), max_length=200, blank=True)
    user = models.ForeignKey(User, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='quick_orders')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'order'
        ordering = ['name', 'user', 'email']
        verbose_name = _('Quick order')
        verbose_name_plural = _('Quick orders')


feature = models.ForeignKey(
    'catalogue.Feature', verbose_name=_('Feature'), related_name='lines_attributes', null=True, blank=True
)
feature.contribute_to_class(LineAttribute, "feature")

product_images = models.ManyToManyField(
    'catalogue.ProductImage', blank=True, related_name='lines_attributes', verbose_name=_('Product images')
)
product_images.contribute_to_class(LineAttribute, "product_images")

LineAttribute._meta.get_field('option').blank = True
LineAttribute._meta.get_field('value').blank = True
LineAttribute._meta.get_field('type').blank = True
