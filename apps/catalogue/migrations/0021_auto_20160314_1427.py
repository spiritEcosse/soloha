# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0020_auto_20160314_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image_banner',
            field=models.ImageField(max_length=255, upload_to=b'categories', null=True, verbose_name='Image banner', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='link_banner',
            field=models.URLField(max_length=255, null=True, verbose_name='Link banner', blank=True),
        ),
    ]
