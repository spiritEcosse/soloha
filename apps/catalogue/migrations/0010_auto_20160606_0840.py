# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160503_0913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='versionattribute',
            name='price_retail',
            field=models.DecimalField(default=0, verbose_name='Price (retail)', max_digits=12, decimal_places=2, blank=True),
        ),
    ]
