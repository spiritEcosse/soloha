# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields
import oscar.core.validators
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20150604_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='Slug')),
                ('sort', models.IntegerField(default=0, null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='Parent', blank=True, to='catalogue.Feature', null=True)),
            ],
            options={
                'ordering': ('sort', 'title', 'id'),
                'abstract': False,
                'verbose_name': 'Feature',
                'verbose_name_plural': 'Features',
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
        migrations.CreateModel(
            name='ProductFeature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort', models.IntegerField(default=0, null=True, verbose_name='Sort', blank=True)),
                ('info', models.CharField(max_length=255, verbose_name='Block info', blank=True)),
                ('feature', models.ForeignKey(related_name='product_features', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='Feature', to='catalogue.Feature')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Product feature',
                'verbose_name_plural': 'Product features',
            },
        ),
        migrations.CreateModel(
            name='ProductOptions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('option', models.ForeignKey(related_name='product_options', to='catalogue.Feature')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Product option',
                'verbose_name_plural': 'Product options',
            },
        ),
        migrations.CreateModel(
            name='ProductVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Product version',
                'verbose_name_plural': 'Product versions',
            },
        ),
        migrations.CreateModel(
            name='VersionAttribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(max_length=255, upload_to=b'products/version/attribute/%Y/%m/%d/', null=True, verbose_name='Image', blank=True)),
                ('attribute', models.ForeignKey(related_name='version_attributes', verbose_name='Attribute', to='catalogue.Feature')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Version attribute',
                'verbose_name_plural': 'Version attributes',
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('sort', 'name', 'id'), 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-views_count'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.RemoveField(
            model_name='product',
            name='product_options',
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
            field=models.ImageField(max_length=255, upload_to=b'categories/%Y/%m/%d/', null=True, verbose_name='Image banner', blank=True),
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
        migrations.AddField(
            model_name='product',
            name='views_count',
            field=models.IntegerField(default=0, verbose_name=b'views count', editable=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.ImageField(max_length=255, upload_to=b'categories/%Y/%m/%d/', null=True, verbose_name='Image', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True, max_length=200, verbose_name='Slug'),
        ),
        migrations.AlterField(
            model_name='product',
            name='attributes',
            field=models.ManyToManyField(related_name='attr_products', verbose_name='Attribute of product', to='catalogue.Feature', through='catalogue.ProductFeature', blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='categories',
            field=models.ManyToManyField(related_name='products', verbose_name='Categories', to='catalogue.Category', blank=True),
        ),
        migrations.AlterField(
            model_name='productattribute',
            name='code',
            field=models.SlugField(max_length=128, verbose_name='Code', validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z_][0-9a-zA-Z_]*$', message="Code can only contain the letters a-z, A-Z, digits, and underscores, and can't start with a digit"), oscar.core.validators.non_python_keyword]),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('slug', 'parent')]),
        ),
        migrations.AddField(
            model_name='versionattribute',
            name='product',
            field=models.ManyToManyField(related_name='version_attributes', verbose_name='Product', to='catalogue.Product', blank=True),
        ),
        migrations.AddField(
            model_name='versionattribute',
            name='version',
            field=models.ForeignKey(related_name='version_attributes', verbose_name='Version of product', to='catalogue.ProductVersion'),
        ),
        migrations.AddField(
            model_name='productversion',
            name='attributes',
            field=models.ManyToManyField(related_name='product_versions', verbose_name='Attributes', through='catalogue.VersionAttribute', to='catalogue.Feature'),
        ),
        migrations.AddField(
            model_name='productversion',
            name='product',
            field=models.ForeignKey(related_name='versions', on_delete=django.db.models.deletion.DO_NOTHING, to='catalogue.Product'),
        ),
        migrations.AddField(
            model_name='productoptions',
            name='product',
            field=models.ForeignKey(related_name='product_options', to='catalogue.Product'),
        ),
        migrations.AddField(
            model_name='productfeature',
            name='product',
            field=models.ForeignKey(related_name='product_features', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='Product', to='catalogue.Product'),
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
        migrations.RemoveField(
            model_name='category',
            name='url',
        ),
        migrations.AddField(
            model_name='product',
            name='characteristics',
            field=models.ManyToManyField(related_name='characteristic_products', verbose_name=b'Characteristics', to='catalogue.Feature', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='filters',
            field=models.ManyToManyField(related_name='filter_products', verbose_name='Filters of product', to='catalogue.Feature', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='versionattribute',
            unique_together=set([('version', 'attribute')]),
        ),
        migrations.AlterUniqueTogether(
            name='productoptions',
            unique_together=set([('product', 'option')]),
        ),
        migrations.AlterUniqueTogether(
            name='productfeature',
            unique_together=set([('product', 'feature')]),
        ),
        migrations.AlterUniqueTogether(
            name='productcategory',
            unique_together=set([('product', 'category')]),
        ),
        migrations.AlterUniqueTogether(
            name='feature',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
