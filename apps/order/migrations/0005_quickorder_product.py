# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20160624_1410'),
        ('order', '0004_quickorder'),
    ]

    operations = [
        migrations.AddField(
            model_name='quickorder',
            name='product',
            field=models.ForeignKey(related_name='quick_orders', default=1, to='catalogue.Product'),
            preserve_default=False,
        ),
    ]
