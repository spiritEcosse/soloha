from django.db import models
from django.contrib.flatpages.models import FlatPage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class InfoPage(FlatPage):
    enable = models.BooleanField(verbose_name=_('Enable'), default=True)
    h1 = models.CharField(verbose_name=_('h1'), blank=True, max_length=255)
    meta_title = models.CharField(verbose_name=_('Meta tag: title'), blank=True, max_length=255)
    meta_description = models.TextField(verbose_name=_('Meta tag: description'), blank=True)
    meta_keywords = models.TextField(verbose_name=_('Meta tag: keywords'), blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'flatpages'

    def get_absolute_url(self):
        link = super(InfoPage, self).get_absolute_url()
        dict_values = {'url': link.lstrip('/')}

        return reverse('pages', kwargs=dict_values)