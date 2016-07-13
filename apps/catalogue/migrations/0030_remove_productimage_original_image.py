# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0029_category_category_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='original_image',
        ),
    ]
