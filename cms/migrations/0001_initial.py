# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.file
import filer.fields.image
import mptt.fields
import tinymce.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('auth', '0008_alter_user_username_max_length'),
        ('filer', '0007_auto_20161016_1055'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField(blank=True, help_text=' File Content', null=True, verbose_name='Content')),
                ('order', models.PositiveSmallIntegerField(verbose_name=b'Position')),
                ('file_link', filer.fields.file.FilerFileField(blank=True, help_text=b'Upload one file doc, xls, pdf, etc...', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='file_content', to='filer.File')),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'file',
            },
        ),
        migrations.CreateModel(
            name='Filelist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField(help_text=b' Descripción del listado de archivos', verbose_name='Content')),
            ],
            options={
                'verbose_name': 'File list',
                'verbose_name_plural': 'file lists',
            },
        ),
        migrations.CreateModel(
            name='Form',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField(help_text='Every line is a field ( Label|name=field_type|default text ) ', verbose_name='Content')),
                ('to', models.TextField(verbose_name='to')),
            ],
            options={
                'verbose_name': 'formulario',
                'verbose_name_plural': 'formularios',
            },
        ),
        migrations.CreateModel(
            name='Gallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('columns', models.PositiveSmallIntegerField(default=0, verbose_name='Columns')),
                ('max_width', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='max width')),
                ('max_height', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='max height')),
                ('is_slider', models.BooleanField(default=False, verbose_name='is slider')),
                ('lightbox', models.BooleanField(default=False, verbose_name='lightbox')),
                ('crop', models.BooleanField(default=False, verbose_name='Crop')),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'Galeria',
            },
        ),
        migrations.CreateModel(
            name='Html',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'html code',
                'verbose_name_plural': 'html codes',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('caption', models.CharField(blank=True, max_length=255, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('width', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('height', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('alt', models.CharField(blank=True, max_length=100, null=True)),
                ('link', models.CharField(blank=True, max_length=255, null=True)),
                ('image', filer.fields.image.FilerImageField(blank=True, help_text=b'Upload a image file jpg, gif y png, (800x600 max)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_content', to=settings.FILER_IMAGE_MODEL)),
            ],
            options={
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
        ),
        migrations.CreateModel(
            name='ImageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('caption', models.CharField(blank=True, max_length=255, null=True, verbose_name='Caption')),
                ('alt', models.CharField(blank=True, max_length=100, null=True, verbose_name='alt')),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
                ('gallery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Gallery', verbose_name='gallery')),
                ('image', filer.fields.image.FilerImageField(help_text=b'Upload and image file jpg, gif y png, (800x600 max)', on_delete=django.db.models.deletion.CASCADE, related_name='image_imagefile', to=settings.FILER_IMAGE_MODEL)),
            ],
            options={
                'verbose_name': 'image file',
                'verbose_name_plural': 'image files',
            },
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField(help_text=b'Cada linea es una vi\xc3\xb1eta', verbose_name='Content')),
                ('is_ordered', models.BooleanField(default=False, verbose_name='ordered list')),
            ],
            options={
                'verbose_name': 'lista',
                'verbose_name_plural': 'listas',
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('slug', models.SlugField(unique=True)),
                ('subtitle', models.CharField(blank=True, max_length=255, null=True, verbose_name='Subtitle')),
                ('description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Description')),
                ('new_tab', models.BooleanField(default=False, verbose_name='Abrir en una nueva pesta\xf1a')),
                ('meta_keywords', models.CharField(blank=True, max_length=255)),
                ('meta_description', models.CharField(blank=True, max_length=255)),
                ('meta_title', models.CharField(blank=True, max_length=255)),
                ('redirect_url', models.CharField(blank=True, max_length=255)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('image', filer.fields.image.FilerImageField(blank=True, help_text=b'Sube una imagen en jpg, gif y png, (800x600 max)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_page', to=settings.FILER_IMAGE_MODEL)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Children', to='cms.Page', verbose_name='Parent')),
                ('visible_for', models.ManyToManyField(blank=True, to='auth.Group')),
            ],
            options={
                'ordering': ['tree_id', 'lft', 'level'],
                'verbose_name': 'p\xe1gina',
                'verbose_name_plural': 'p\xe1ginas',
            },
        ),
        migrations.CreateModel(
            name='PageRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('sorting', models.PositiveSmallIntegerField(default=0)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cms.Page')),
            ],
            options={
                'ordering': ['sorting'],
            },
        ),
        migrations.CreateModel(
            name='Table',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', models.TextField(help_text='Every line is a row (cell 1| cell 2 | cell 3)', verbose_name='Table content')),
                ('has_header', models.BooleanField(default=False, verbose_name='has header')),
            ],
            options={
                'verbose_name': 'table',
                'verbose_name_plural': 'tables',
            },
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('content', tinymce.models.HTMLField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Text',
                'verbose_name_plural': 'Texts',
            },
        ),
        migrations.CreateModel(
            name='TextImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.BooleanField(default=False, verbose_name='Remove')),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('date_time_add', models.DateTimeField(auto_now_add=True, null=True)),
                ('date_time_update', models.DateTimeField(auto_now=True, null=True)),
                ('text_ptr_id', models.PositiveSmallIntegerField(default=0, verbose_name='ptr_id')),
                ('content', tinymce.models.HTMLField()),
                ('image', filer.fields.image.FilerImageField(blank=True, default=None, help_text=' Upload an image file jpg, gif y png, (800x600 max)', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='textimage_content', to=settings.FILER_IMAGE_MODEL)),
            ],
            options={
                'verbose_name': 'image and text',
                'verbose_name_plural': 'image and text contents',
            },
        ),
        migrations.AddField(
            model_name='file',
            name='file_list',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cms.Filelist'),
        ),
    ]
