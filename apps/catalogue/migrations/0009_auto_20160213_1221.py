# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160111_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattributevalue',
            name='pos_attribute',
            field=models.BooleanField(default=False, verbose_name='This is attribute'),
        ),
        migrations.AddField(
            model_name='productattributevalue',
            name='pos_characteristic',
            field=models.BooleanField(default=False, verbose_name='This is characteristic'),
        ),
        migrations.AddField(
            model_name='productattributevalue',
            name='pos_filter',
            field=models.BooleanField(default=False, verbose_name='This is filter'),
        ),
        migrations.AddField(
            model_name='productattributevalue',
            name='pos_option',
            field=models.BooleanField(default=False, verbose_name='This is option'),
        ),
    ]
