# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20160704_1831'),
        ('catalogue', '0026_auto_20160712_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category_image',
            field=filer.fields.image.FilerImageField(related_name='category_image', verbose_name='Image', blank=True, to='filer.Image', null=True),
        ),
    ]
