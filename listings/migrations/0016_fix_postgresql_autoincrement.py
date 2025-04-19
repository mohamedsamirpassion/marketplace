from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('listings', '0015_fix_favorite'),  # Make sure this matches your previous migration
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- This SQL only runs in PostgreSQL
            DO $$
            BEGIN
                -- Only execute if this is PostgreSQL
                IF current_setting('server_version_num')::integer >= 90500 THEN
                    -- Fix tables that might have issues with AUTOINCREMENT
                    -- Add more tables as needed
                    PERFORM setval(pg_get_serial_sequence('listings_listing', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_listing;
                    PERFORM setval(pg_get_serial_sequence('listings_listingimage', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_listingimage;
                    PERFORM setval(pg_get_serial_sequence('listings_brand', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_brand;
                    PERFORM setval(pg_get_serial_sequence('listings_model', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_model;
                    PERFORM setval(pg_get_serial_sequence('listings_favorite', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_favorite;
                    PERFORM setval(pg_get_serial_sequence('listings_pendingbrand', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_pendingbrand;
                    PERFORM setval(pg_get_serial_sequence('listings_pendingmodel', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_pendingmodel;
                    PERFORM setval(pg_get_serial_sequence('listings_adspace', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_adspace;
                    PERFORM setval(pg_get_serial_sequence('listings_listingreport', 'id'), coalesce(max(id), 0) + 1, false) FROM listings_listingreport;
                END IF;
            END
            $$;
            """,
            reverse_sql="-- No reverse SQL needed"
        ),
    ] 