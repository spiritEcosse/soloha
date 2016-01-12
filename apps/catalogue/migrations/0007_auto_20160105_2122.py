# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160105_2057'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='enable',
            field=models.BooleanField(default=True, verbose_name='Enable'),
        ),
        migrations.AddField(
            model_name='category',
            name='h1',
            field=models.CharField(max_length=255, verbose_name='h1', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_description',
            field=models.TextField(verbose_name='Meta tag: description', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keywords',
            field=models.TextField(verbose_name='Meta tag: keywords', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title',
            field=models.CharField(max_length=255, verbose_name='Meta tag: title', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='sort',
            field=models.IntegerField(default=0, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='enable',
            field=models.BooleanField(default=True, verbose_name='Enable'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1',
            field=models.CharField(max_length=255, verbose_name='h1', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_description',
            field=models.TextField(verbose_name='Meta tag: description', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keywords',
            field=models.TextField(verbose_name='Meta tag: keywords', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title',
            field=models.CharField(max_length=255, verbose_name='Meta tag: title', blank=True),
        ),
    ]
