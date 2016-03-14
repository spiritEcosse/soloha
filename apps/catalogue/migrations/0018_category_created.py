# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0017_category_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 14, 13, 1, 16, 268746, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
