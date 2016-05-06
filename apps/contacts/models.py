from django.db import models


class ContactUs(models.Model):
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=19, blank=True)
    email = models.EmailField(max_length=200, blank=True)
    comment = models.CharField(max_length=200)

    # from django.core.validators import RegexValidator
    #
    # class PhoneModel(models.Model):
    #     ...
    #     phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
    #                                  message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    #     phone_number = models.CharField(validators=[phone_regex], blank=True)