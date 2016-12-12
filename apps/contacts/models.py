from django.db import models


class ContactUs(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=19, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    comment = models.CharField(max_length=200)
