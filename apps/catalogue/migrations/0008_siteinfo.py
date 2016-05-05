# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('catalogue', '0007_auto_20160421_1606'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteInfo',
            fields=[
                ('site_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sites.Site')),
                ('work_time', models.CharField(max_length=1000)),
                ('address', models.CharField(max_length=1000)),
                ('phone_number', django.contrib.postgres.fields.ArrayField(size=None, base_field=models.CharField(max_length=1000), blank=True)),
                ('email', models.EmailField(max_length=200, blank=True)),
            ],
            bases=('sites.site',),
        ),
    ]
