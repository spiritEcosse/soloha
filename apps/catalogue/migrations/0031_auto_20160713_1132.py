# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0030_remove_productimage_original_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='original_image',
            field=models.ImageField(max_length=255, upload_to=b'images/products/%Y/%m/', null=True, verbose_name='Original', blank=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='original',
            field=filer.fields.image.FilerImageField(related_name='original', verbose_name='Original', blank=True, to='filer.Image', null=True),
        ),
    ]
