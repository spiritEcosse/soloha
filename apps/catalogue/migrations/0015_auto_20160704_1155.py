# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_auto_20160704_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='h1',
            field=models.CharField(max_length=300, verbose_name='h1', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(max_length=500, upload_to=b'categories/%Y/%m/%d/', null=True, verbose_name='Image', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='image_banner',
            field=models.ImageField(max_length=600, upload_to=b'categories/%Y/%m/%d/', null=True, verbose_name='Image banner', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=500, verbose_name='Name', db_index=True),
        ),
    ]
