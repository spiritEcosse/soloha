# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('filer', '0007_auto_20160704_1831'),
        ('catalogue', '0027_category_category_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='category_image',
        ),
        migrations.AddField(
            model_name='productimage',
            name='original_image',
            field=filer.fields.image.FilerImageField(related_name='original', verbose_name='Original', blank=True, to='filer.Image', null=True),
        ),
    ]
