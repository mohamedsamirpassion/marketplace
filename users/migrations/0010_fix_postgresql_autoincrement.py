from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # Changed to reference the initial migration
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- This SQL only runs in PostgreSQL
            DO $$
            BEGIN
                -- Only execute if this is PostgreSQL
                IF current_setting('server_version_num')::integer >= 90500 THEN
                    -- Fix user tables that might have issues with AUTOINCREMENT
                    PERFORM setval(pg_get_serial_sequence('users_user', 'id'), coalesce(max(id), 0) + 1, false) FROM users_user;
                END IF;
            END
            $$;
            """,
            reverse_sql="-- No reverse SQL needed"
        ),
    ] 