# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0015_auto_20160704_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='h1',
            field=models.CharField(max_length=310, verbose_name='h1', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.ImageField(max_length=455, upload_to=b'categories', null=True, verbose_name='Icon', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='link_banner',
            field=models.URLField(max_length=555, null=True, verbose_name='Link banner', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='meta_title',
            field=models.CharField(max_length=255, verbose_name='Meta tag: title', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=300, verbose_name='Name', db_index=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True, max_length=400, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='product',
            name='h1',
            field=models.CharField(max_length=310, verbose_name='h1', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='meta_title',
            field=models.CharField(max_length=320, verbose_name='Meta tag: title', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='slug',
            field=models.SlugField(unique=True, max_length=400, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=300, verbose_name='Title'),
        ),
    ]
