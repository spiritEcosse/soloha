from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField


@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    work_time = models.CharField(verbose_name=_('Work time'), max_length=1000)
    address = models.CharField(verbose_name=_('Actual address'), max_length=1000)
    phone_numbers = models.ManyToManyField('sites.PhoneNumber', verbose_name=_('Phone numbers'), blank=True)
    email = models.EmailField(verbose_name=_('Email'), max_length=200)
    shop_short_desc = models.CharField(verbose_name=_('Short description of shop'), max_length=200, blank=True)
    way = RichTextUploadingField(verbose_name=_('Way to us'), blank=True)
    map = RichTextUploadingField(verbose_name=_('Map google'))

    def __str__(self):
        return self.site.domain

    class Meta:
        app_label = 'sites'
        verbose_name = _('Information')
        verbose_name_plural = _('Information')

    def phone_numbers_slice(self):
        return self.phone_numbers.all()[:4]


class PhoneNumberManager(models.Manager):
    def browse(self):
        return self.get_queryset().only(
            'phone_number',
        )


class PhoneNumber(models.Model):
    phone_number = PhoneNumberField(verbose_name=_('Phone number'), blank=True)
    objects = PhoneNumberManager()

    class Meta:
        app_label = 'sites'
        verbose_name = _('Phone number')
        verbose_name_plural = _('Phone numbers')

    def __str__(self):
        return self.phone_number.as_international
