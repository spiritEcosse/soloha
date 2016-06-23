# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_quickorder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quickorder',
            name='phone_number',
            field=models.CharField(max_length=19, verbose_name='Phone number client'),
        ),
    ]
