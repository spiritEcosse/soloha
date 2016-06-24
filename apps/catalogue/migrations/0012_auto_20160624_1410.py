# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_auto_20160623_1500'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quickorder',
            name='user',
        ),
        migrations.DeleteModel(
            name='QuickOrder',
        ),
    ]
