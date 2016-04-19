# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_remove_feature_enable'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='productfeature',
            unique_together=set([('product', 'feature')]),
        ),
        migrations.AlterUniqueTogether(
            name='productoptions',
            unique_together=set([('product', 'option')]),
        ),
    ]
