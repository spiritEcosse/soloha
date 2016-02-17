# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20160213_2045'),
    ]

    operations = [
        migrations.AddField(
            model_name='productattributevalue',
            name='value_option_multi',
            field=models.ManyToManyField(related_name='product_attribute_values', null=True, verbose_name='Multi value option', to='catalogue.AttributeOption', blank=True),
        ),
    ]
