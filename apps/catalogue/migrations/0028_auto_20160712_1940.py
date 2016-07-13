# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0027_category_category_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='original',
            field=filer.fields.image.FilerImageField(related_name='original', verbose_name='Original', blank=True, to='filer.Image', null=True),
        ),
    ]
