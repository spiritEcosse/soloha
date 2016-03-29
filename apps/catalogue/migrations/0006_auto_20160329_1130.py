# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import django.core.validators
import oscar.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20150604_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('sort', models.IntegerField(default=0, null=True, blank=True)),
                ('enable', models.BooleanField(default=True, verbose_name='Enable')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='catalogue.Filter', null=True)),
            ],
            options={
                'ordering': ('sort', 'title', 'id'),
                'abstract': False,
                'verbose_name': 'Filter',
                'verbose_name_plural': 'Filters',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ['product', 'category'],
                'abstract': False,
                'verbose_name': 'Product category',
                'verbose_name_plural': 'Product categories',
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('sort', 'name', 'id'), 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.RemoveField(
            model_name='category',
            name='url',
        ),
        migrations.AddField(
            model_name='category',
            name='enable',
            field=models.BooleanField(default=True, verbose_name='Enable'),
        ),
        migrations.AddField(
            model_name='category',
            name='h1',
            field=models.CharField(max_length=255, verbose_name='h1', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='icon',
            field=models.ImageField(max_length=255, upload_to=b'categories', null=True, verbose_name='Icon', blank=True),
        ),
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
        migrations.AddField(
            model_name='category',
            name='meta_description',
            field=models.TextField(verbose_name='Meta tag: description', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_keywords',
            field=models.TextField(verbose_name='Meta tag: keywords', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='meta_title',
            field=models.CharField(max_length=255, verbose_name='Meta tag: title', blank=True),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='catalogue.Category', null=True),
        ),
        migrations.AddField(
            model_name='category',
            name='sort',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='enable',
            field=models.BooleanField(default=True, verbose_name='Enable'),
        ),
        migrations.AddField(
            model_name='product',
            name='h1',
            field=models.CharField(max_length=255, verbose_name='h1', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_description',
            field=models.TextField(verbose_name='Meta tag: description', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_keywords',
            field=models.TextField(verbose_name='Meta tag: keywords', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='meta_title',
            field=models.CharField(max_length=255, verbose_name='Meta tag: title', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True, max_length=200, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='code',
            field=models.SlugField(max_length=128, verbose_name='Code', validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z_][0-9a-zA-Z_]*$', message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit"), oscar.core.validators.non_python_keyword]),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='category',
            field=models.ForeignKey(verbose_name='Category', to='catalogue.Category'),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='product',
            field=models.ForeignKey(verbose_name='Product', to='catalogue.Product'),
        ),
        migrations.AddField(
            model_name='product',
            name='filters',
            field=models.ManyToManyField(to='catalogue.Filter', verbose_name='Filters of product'),
        ),
        migrations.AlterUniqueTogether(
            name='productcategory',
            unique_together=set([('product', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='filter',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
