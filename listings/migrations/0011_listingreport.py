# Generated by Django 5.1.7 on 2025-04-13 00:32

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0010_listing_is_sold_listing_sold_date'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ListingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('spam', 'Spam or Misleading'), ('fraud', 'Fraudulent Listing'), ('offensive', 'Offensive Content'), ('wrong_info', 'Incorrect Information'), ('fake_images', 'Fake Images'), ('other', 'Other')], max_length=20)),
                ('comment', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending Review'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending', max_length=20)),
                ('admin_note', models.TextField(blank=True)),
                ('reported_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('resolved_on', models.DateTimeField(blank=True, null=True)),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='listings.listing')),
                ('reporter', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_listings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
