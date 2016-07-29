# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=255, verbose_name='Email')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('city', models.CharField(max_length=50, verbose_name='City')),
            ],
        ),
    ]
