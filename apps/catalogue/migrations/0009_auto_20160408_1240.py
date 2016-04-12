# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160404_0753'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-views_count'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AddField(
            model_name='product',
            name='views_count',
            field=models.IntegerField(default=0, verbose_name=b'views count', editable=False),
        ),
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
    ]
