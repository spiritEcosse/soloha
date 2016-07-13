from oscar.apps.order.models import *  # noqa
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.db import models
from oscar.core.loading import get_model

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
