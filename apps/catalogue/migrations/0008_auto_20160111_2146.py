# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20160105_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='sort',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
