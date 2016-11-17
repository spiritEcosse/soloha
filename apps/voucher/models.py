from oscar.apps.voucher.abstract_models import AbstractVoucher
from django.db import models


class ProductiveVoucherManager(models.Manager):
    def browse(self):
        return self.get_queryset().only(
            'name'
        ).order_by()


class Voucher(AbstractVoucher):
    objects = ProductiveVoucherManager()


from oscar.apps.voucher.models import *  # noqa
