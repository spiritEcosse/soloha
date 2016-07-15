# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0031_auto_20160713_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='filters',
            field=models.ManyToManyField(related_name='filter_products', null=True, verbose_name='Filters of product', to='catalogue.Feature', blank=True),
        ),
    ]
