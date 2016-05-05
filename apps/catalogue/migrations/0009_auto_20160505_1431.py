# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
        ('order', '0003_auto_20150113_1629'),
        ('catalogue', '0008_siteinfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='siteinfo',
            name='site_ptr',
        ),
        migrations.DeleteModel(
            name='SiteInfo',
        ),
    ]
