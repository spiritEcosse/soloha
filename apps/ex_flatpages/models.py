from django.db import models
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags


class InfoPage(models.Model):
    GLYPHICON_CHOICES = (
        ('car', 'icon-car'),
        ('pay', 'icon-pay'),
        ('manager', 'icon-manager'),
    )
    flatpage = models.OneToOneField(FlatPage, on_delete=models.CASCADE, related_name='info', primary_key=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=20, choices=GLYPHICON_CHOICES, blank=True)

    class Meta:
        app_label = 'flatpages'

    def get_meta_description(self):
        return self.meta_description or truncatechars(strip_tags(self.flatpage.content), 100)

    def get_h1(self):
        return self.h1 or self.flatpage.title

    def get_meta_title(self):
        return self.meta_title or self.flatpage.title
