# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_productattributevalue_value_option_multi'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productattributevalue',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='productattributevalue',
            unique_together=set([]),
        ),
    ]
