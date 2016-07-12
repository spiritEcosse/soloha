# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0021_auto_20160712_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=ckeditor.fields.RichTextField(verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=ckeditor.fields.RichTextField(verbose_name='Description', blank=True),
        ),
    ]
