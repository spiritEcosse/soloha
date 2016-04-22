# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160419_1406'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productfeature',
            options={'ordering': ['sort', 'feature__title'], 'verbose_name': 'Product feature', 'verbose_name_plural': 'Product features'},
        ),
    ]
