# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20160624_1410'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='versionattribute',
            name='image',
        ),
        migrations.RemoveField(
            model_name='versionattribute',
            name='product',
        ),
        migrations.AddField(
            model_name='productfeature',
            name='image',
            field=models.ImageField(max_length=255, upload_to=b'products/feature/%Y/%m/%d/', null=True, verbose_name='Image', blank=True),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='product_with_images',
            field=models.ManyToManyField(related_name='product_feature', verbose_name='Product', to='catalogue.Product', blank=True),
        ),
    ]
