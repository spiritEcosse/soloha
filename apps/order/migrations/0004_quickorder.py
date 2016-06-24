# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0003_auto_20150113_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuickOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name client')),
                ('phone_number', models.CharField(max_length=19, verbose_name='Phone number client')),
                ('email', models.EmailField(max_length=200, verbose_name='Email client', blank=True)),
                ('comment', models.CharField(max_length=200, verbose_name='Comment client', blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name', 'user', 'email'],
                'verbose_name': 'Quick order',
                'verbose_name_plural': 'Quick orders',
            },
        ),
    ]
