# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0022_auto_20160315_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='url',
            field=models.URLField(default='', verbose_name='Full slug', max_length=1000, editable=False),
            preserve_default=False,
        ),
    ]
