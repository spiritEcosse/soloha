# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0021_auto_20160314_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='sort',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
    ]
