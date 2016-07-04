# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_auto_20160627_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='meta_title',
            field=models.CharField(max_length=1000, verbose_name='Meta tag: title', blank=True),
        ),
    ]
