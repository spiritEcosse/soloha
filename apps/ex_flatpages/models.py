from django.contrib.flatpages.models import FlatPage
from django.template.defaultfilters import truncatechars
from django.utils.html import strip_tags
from django.utils.text import capfirst
from django.core.urlresolvers import get_script_prefix
from django.db import models
from django.utils.encoding import iri_to_uri, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


@python_2_unicode_compatible
class InfoPage(models.Model):
    GLYPHICON_CHOICES = (
        ('car', 'icon-car'),
        ('pay', 'icon-pay'),
        ('manager', 'icon-manager'),
    )
    FOOTER = 'footer'
    HEADER = 'header'
    POSITION_CHOICES = (
        (HEADER, capfirst(HEADER)),
        (FOOTER, capfirst(FOOTER)),
    )
    flatpage = models.OneToOneField(FlatPage, on_delete=models.CASCADE, related_name='info', primary_key=True)
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    created = models.DateTimeField(auto_now_add=True)
    icon = models.CharField(max_length=20, choices=GLYPHICON_CHOICES, blank=True)
    position = models.CharField(choices=POSITION_CHOICES, max_length=20, blank=True)

    class Meta:
        app_label = 'flatpages'

    def __str__(self):
        return "%s -- %s" % (self.url, self.title)

    def get_meta_description(self):
        return self.meta_description or truncatechars(strip_tags(self.flatpage.content), 100)

    def get_h1(self):
        return self.h1 or self.flatpage.title

    def get_meta_title(self):
        return self.meta_title or self.flatpage.title

    def url(self):
        return self.flatpage.url

    def title(self):
        return self.flatpage.title

    def get_absolute_url(self):
        return iri_to_uri(get_script_prefix() + self.flatpage.url.strip(get_script_prefix()) + get_script_prefix())
