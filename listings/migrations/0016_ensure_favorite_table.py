from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0015_fix_favorite'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the table if it exists
            "DROP TABLE IF EXISTS listings_favorite;",
            # No reverse operation since we're just recreating it
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS "listings_favorite" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "date_added" datetime NOT NULL,
                "listing_id" integer NOT NULL REFERENCES "listings_listing" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer NOT NULL REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED,
                UNIQUE ("user_id", "listing_id")
            );
            """,
            # Reverse SQL to drop the table
            "DROP TABLE IF EXISTS listings_favorite;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX "listings_favorite_listing_id" ON "listings_favorite" ("listing_id");
            """,
            # No reverse operation needed
            "SELECT 1;"
        ),
        migrations.RunSQL(
            """
            CREATE INDEX "listings_favorite_user_id" ON "listings_favorite" ("user_id");
            """,
            # No reverse operation needed
            "SELECT 1;"
        ),
    ] 