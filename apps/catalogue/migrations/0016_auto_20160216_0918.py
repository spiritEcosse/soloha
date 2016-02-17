# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0015_remove_productattribute_value_option_multi'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productattributevalue',
            options={'verbose_name': 'Product attribute value', 'verbose_name_plural': 'Product attribute values'},
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='pos_attribute',
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='pos_characteristic',
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='pos_filter',
        ),
        migrations.RemoveField(
            model_name='productattribute',
            name='pos_option',
        ),
        migrations.AlterUniqueTogether(
            name='productattributevalue',
            unique_together=set([('attribute', 'product')]),
        ),
    ]
