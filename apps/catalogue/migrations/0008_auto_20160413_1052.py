# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20160412_1656'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='versionattribute',
            unique_together=set([('version', 'attribute')]),
        ),
    ]
