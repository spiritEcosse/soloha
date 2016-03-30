# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160329_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(to='catalogue.Category', null=True, verbose_name='Categories', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='filters',
            field=models.ManyToManyField(to='catalogue.Filter', null=True, verbose_name='Filters of product', blank=True),
        ),
    ]
