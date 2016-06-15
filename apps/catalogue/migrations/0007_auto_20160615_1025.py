# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160609_1532'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productversion',
            name='plus',
        ),
        migrations.RemoveField(
            model_name='versionattribute',
            name='plus',
        ),
        migrations.AddField(
            model_name='product',
            name='non_standard_cost_price',
            field=models.DecimalField(null=True, verbose_name='Non-standard cost price', max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='non_standard_price_retail',
            field=models.DecimalField(null=True, verbose_name='Non-standard retail price', max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='non_standard',
            field=models.BooleanField(default=False, verbose_name='Available non standard size for this feature'),
        ),
        migrations.AlterField(
            model_name='versionattribute',
            name='cost_price',
            field=models.DecimalField(default=0, verbose_name='Cost Price', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
