# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0014_auto_20160215_2012'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productattribute',
            name='value_option_multi',
        ),
    ]
