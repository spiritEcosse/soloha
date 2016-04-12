# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_auto_20160412_1316'),
        ('partner', '0003_auto_20150604_1450'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockrecord',
            name='percent',
            field=models.IntegerField(default=0, null=True, verbose_name='Percent', blank=True),
        ),
        migrations.AddField(
            model_name='stockrecord',
            name='plus',
            field=models.BooleanField(default=False, verbose_name='Plus on main price'),
        ),
        migrations.AddField(
            model_name='stockrecord',
            name='product_options',
            field=models.ForeignKey(related_name='stockrecords', verbose_name='Product options', blank=True, to='catalogue.ProductOptions', null=True),
        ),
        migrations.AddField(
            model_name='stockrecord',
            name='product_version',
            field=models.ForeignKey(related_name='stockrecords', verbose_name='Product version', blank=True, to='catalogue.ProductVersion', null=True),
        ),
    ]
