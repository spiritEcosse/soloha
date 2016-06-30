from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    work_time = models.CharField(verbose_name=_('Work time'), max_length=1000)
    address = models.CharField(verbose_name=_('Actual address'), max_length=1000)
    phone_number = models.CharField(verbose_name=_('Phone number'), max_length=19, blank=True)
    email = models.EmailField(verbose_name=_('Email'), max_length=200)
    shop_short_desc = models.CharField(verbose_name=_('Short description of shop'), max_length=200, blank=True)

    def __str__(self):
        return self.site.domain

    class Meta:
        app_label = 'sites'
