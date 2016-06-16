# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160616_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='bottom_line',
            field=models.IntegerField(null=True, verbose_name='Bottom line size', blank=True),
        ),
        migrations.AddField(
            model_name='feature',
            name='top_line',
            field=models.IntegerField(null=True, verbose_name='Top line size', blank=True),
        ),
    ]
