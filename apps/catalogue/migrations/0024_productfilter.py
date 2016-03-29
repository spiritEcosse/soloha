# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_category_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFilter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name=b'Filter name')),
                ('parent', models.ManyToManyField(related_name='_productfilter_parent_+', null=True, to='catalogue.ProductFilter', blank=True)),
                ('product', models.ManyToManyField(to='catalogue.Product')),
            ],
        ),
    ]
