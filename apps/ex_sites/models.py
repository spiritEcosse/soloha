from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor_uploader.fields import RichTextUploadingField
from filer.fields.image import FilerImageField


@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    work_time = models.CharField(verbose_name=_('Work time'), max_length=1000)
    address = models.CharField(verbose_name=_('Actual address'), max_length=1000)
    phone_numbers = models.ManyToManyField('sites.PhoneNumber', verbose_name=_('Phone numbers'), blank=True, related_name='info_site'
                                                                                                                          ''
                                                                                                                          '')
    email = models.EmailField(verbose_name=_('Email'), max_length=200)
    shop_short_desc = models.CharField(verbose_name=_('Short description of shop'), max_length=200, blank=True)
    way = RichTextUploadingField(verbose_name=_('Way to us'), blank=True)
    map = RichTextUploadingField(verbose_name=_('Map google'))
    google_analytics = models.TextField(verbose_name=_('Google Analytics'), blank=True)
    yandex_verification = models.CharField(verbose_name=_('Yandex verification'), blank=True, max_length=500)
    google_verification = models.CharField(verbose_name=_('Google verification'), blank=True, max_length=500)
    fast_call = models.TextField(verbose_name=_('Fast call'), blank=True)
    chat = models.TextField(verbose_name=_('Chat'), blank=True)

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
    icon = FilerImageField(verbose_name=_('Icon'), blank=True, null=True, related_name='phone_number_icon')
    objects = PhoneNumberManager()

    class Meta:
        app_label = 'sites'
        verbose_name = _('Phone number')
        verbose_name_plural = _('Phone numbers')

    def __str__(self):
        return self.phone_number.as_international
