from django.db import models
from django.utils.translation import pgettext_lazy


class Subscribe(models.Model):
    email = models.EmailField(pgettext_lazy(u'User email', u'Email'), max_length=255)
    name = models.CharField(pgettext_lazy(u'User name', u'Name'), max_length=50)
    city = models.CharField(pgettext_lazy(u'User city', u'City'), max_length=50)
