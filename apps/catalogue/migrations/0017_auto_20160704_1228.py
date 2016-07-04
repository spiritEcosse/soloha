# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0016_auto_20160704_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='meta_title',
            field=models.CharField(max_length=480, verbose_name='Meta tag: title', blank=True),
        ),
    ]
