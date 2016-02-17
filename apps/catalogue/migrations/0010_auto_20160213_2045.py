# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160213_1221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productattributevalue',
            name='pos_attribute',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is attribute'),
        ),
        migrations.AlterField(
            model_name='productattributevalue',
            name='pos_characteristic',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is characteristic'),
        ),
        migrations.AlterField(
            model_name='productattributevalue',
            name='pos_filter',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is filter'),
        ),
        migrations.AlterField(
            model_name='productattributevalue',
            name='pos_option',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is option'),
        ),
    ]
