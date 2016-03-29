# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0024_productfilter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productfilter',
            name='product',
        ),
        migrations.AddField(
            model_name='product',
            name='product_filter',
            field=models.ManyToManyField(to='catalogue.ProductFilter'),
        ),
    ]
