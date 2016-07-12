# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor_uploader.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0023_auto_20160712_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Description', blank=True),
        ),
    ]
