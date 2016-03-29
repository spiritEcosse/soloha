# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0025_auto_20160325_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfilter',
            name='name',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Filter name'),
        ),
    ]
