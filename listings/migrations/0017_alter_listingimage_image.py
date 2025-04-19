# Generated by Django 5.1.7 on 2025-04-19 00:04

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0016_ensure_favorite_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listingimage',
            name='image',
            field=cloudinary.models.CloudinaryField(max_length=255, verbose_name='image'),
        ),
    ]
