# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20160215_0756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productattributevalue',
            name='pos_attribute',
        ),
        migrations.RemoveField(
            model_name='productattributevalue',
            name='pos_characteristic',
        ),
        migrations.RemoveField(
            model_name='productattributevalue',
            name='pos_filter',
        ),
        migrations.RemoveField(
            model_name='productattributevalue',
            name='pos_option',
        ),
        migrations.RemoveField(
            model_name='productattributevalue',
            name='value_option_multi',
        ),
        migrations.AddField(
            model_name='productclass',
            name='pos_attribute',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is attribute'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='pos_characteristic',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is characteristic'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='pos_filter',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is filter'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='pos_option',
            field=models.BooleanField(default=False, db_index=True, verbose_name='This is option'),
        ),
        migrations.AddField(
            model_name='productclass',
            name='value_option_multi',
            field=models.ManyToManyField(related_name='product_attribute_values', null=True, verbose_name='Multi value option', to='catalogue.AttributeOption', blank=True),
        ),
    ]
