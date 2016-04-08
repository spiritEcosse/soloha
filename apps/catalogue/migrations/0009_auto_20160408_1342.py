# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160404_0753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(related_name='products', null=True, verbose_name='Categories', to='catalogue.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='filters',
            field=models.ManyToManyField(related_name='products', null=True, verbose_name='Filters of product', to='catalogue.Filter', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(unique=True, max_length=255, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Title'),
        ),
    ]
