# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160503_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionattribute',
            name='cost_price',
            field=models.DecimalField(null=True, verbose_name='Cost Price', max_digits=12, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='versionattribute',
            name='price_retail',
            field=models.DecimalField(null=True, verbose_name='Price (retail)', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
