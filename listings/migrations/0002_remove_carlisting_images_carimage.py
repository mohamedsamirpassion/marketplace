# Generated by Django 4.2.3 on 2025-03-26 13:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='carlisting',
            name='images',
        ),
        migrations.CreateModel(
            name='CarImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='car_images/')),
                ('car_listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='listings.carlisting')),
            ],
        ),
    ]
