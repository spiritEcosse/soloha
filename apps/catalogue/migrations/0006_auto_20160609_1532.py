# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20160510_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='productversion',
            name='plus',
            field=models.BooleanField(default=False, verbose_name='Plus on price'),
        ),
        migrations.AddField(
            model_name='versionattribute',
            name='cost_price',
            field=models.DecimalField(null=True, verbose_name='Cost Price', max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='versionattribute',
            name='plus',
            field=models.BooleanField(default=False, verbose_name='Plus on price'),
        ),
        migrations.AddField(
            model_name='versionattribute',
            name='price_retail',
            field=models.DecimalField(default=0, verbose_name='Price (retail)', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
