from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is created to fix the AUTO INCREMENT issue specifically for PostgreSQL.
    """
    
    dependencies = [
        ('listings', '0018_merge_20250419_migration'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL that runs for PostgreSQL - recreates the favorite table with proper sequence
            sql="""
            -- Only run this if using PostgreSQL, skip for SQLite
            DO $$
            BEGIN
                -- Check if we're using PostgreSQL
                IF current_setting('server_version_num')::integer > 0 THEN
                    -- Drop the table if it exists
                    DROP TABLE IF EXISTS "listings_favorite";
                    
                    -- Create a correct PostgreSQL sequence for the ID
                    DROP SEQUENCE IF EXISTS listings_favorite_id_seq;
                    CREATE SEQUENCE listings_favorite_id_seq;
                    
                    -- Create the table with PostgreSQL-compatible auto-incrementing ID
                    CREATE TABLE "listings_favorite" (
                        "id" integer NOT NULL DEFAULT nextval('listings_favorite_id_seq'),
                        "date_added" timestamp with time zone NOT NULL,
                        "listing_id" integer NOT NULL,
                        "user_id" integer NOT NULL,
                        CONSTRAINT listings_favorite_pkey PRIMARY KEY ("id"),
                        CONSTRAINT listings_favorite_user_id_listing_id_key UNIQUE ("user_id", "listing_id"),
                        CONSTRAINT listings_favorite_listing_id_fkey FOREIGN KEY ("listing_id") REFERENCES "listings_listing" ("id") DEFERRABLE INITIALLY DEFERRED,
                        CONSTRAINT listings_favorite_user_id_fkey FOREIGN KEY ("user_id") REFERENCES "users_user" ("id") DEFERRABLE INITIALLY DEFERRED
                    );
                    
                    -- Set the sequence to be owned by the table
                    ALTER SEQUENCE listings_favorite_id_seq OWNED BY listings_favorite.id;
                END IF;
            END $$;
            """,
            # No reverse SQL needed since this is fixing an error condition
            reverse_sql="-- No reverse SQL needed for this fix"
        ),
    ] 