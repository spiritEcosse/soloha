from django.utils.encoding import python_2_unicode_compatible
from django.contrib.sites.models import Site
from django.db import models


@python_2_unicode_compatible
class Info(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, related_name='info')
    work_time = models.CharField(max_length=1000)
    address = models.CharField(max_length=1000)
    phone_number = models.CharField(max_length=19, blank=True)
    email = models.EmailField(max_length=200)

    def __str__(self):
        return self.site.domain

    class Meta:
        app_label = 'sites'
