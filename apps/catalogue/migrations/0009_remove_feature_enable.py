# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160413_1052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feature',
            name='enable',
        ),
    ]
