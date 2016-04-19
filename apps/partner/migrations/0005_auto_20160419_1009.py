# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0004_auto_20160412_1316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockrecord',
            name='partner',
            field=models.ForeignKey(related_name='stockrecords', verbose_name='Partner', blank=True, to='partner.Partner', null=True),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='product',
            field=models.ForeignKey(related_name='stockrecords', verbose_name='Product', blank=True, to='catalogue.Product', null=True),
        ),
    ]
