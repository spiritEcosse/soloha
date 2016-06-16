# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20160615_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='non_standard_cost_price',
            field=models.DecimalField(default=0, verbose_name='Non-standard cost price', max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='non_standard_price_retail',
            field=models.DecimalField(default=0, verbose_name='Non-standard retail price', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
