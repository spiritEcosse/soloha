# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partner', '0003_auto_20150604_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockrecord',
            name='partner',
            field=models.ForeignKey(related_name='stockrecords', verbose_name='Partner', blank=True, to='partner.Partner', null=True),
        ),
        migrations.AlterField(
            model_name='stockrecord',
            name='partner_sku',
            field=models.CharField(max_length=128, verbose_name='Partner SKU', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='stockrecord',
            unique_together=set([]),
        ),
    ]
