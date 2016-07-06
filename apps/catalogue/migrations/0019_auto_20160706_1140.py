# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0018_auto_20160704_1237'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-views_count', 'title', 'pk'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
    ]
