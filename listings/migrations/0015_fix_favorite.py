# Generated by Django 5.1.7 on 2025-04-13 15:12

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('listings', '0014_brand_name_ar_model_name_ar_alter_listing_fuel_type'),
    ]

    operations = [
        migrations.RunSQL(
            # First check if the table already exists and drop it if it does
            """
            DROP TABLE IF EXISTS "listings_favorite";
            """,
            # Reverse SQL (do nothing)
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            CREATE TABLE "listings_favorite" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "date_added" datetime NOT NULL,
                "listing_id" integer NOT NULL REFERENCES "listings_listing" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer NOT NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                UNIQUE ("user_id", "listing_id")
            );
            """,
            # Reverse SQL
            """
            DROP TABLE IF EXISTS "listings_favorite";
            """
        ),
        migrations.RunSQL(
            """
            CREATE INDEX "listings_favorite_listing_id" ON "listings_favorite" ("listing_id");
            """,
            # Reverse SQL
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX "listings_favorite_user_id" ON "listings_favorite" ("user_id");
            """,
            # Reverse SQL
            "SELECT 1;"
        ),
    ]
