from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is created to bypass problematic migrations.
    """
    
    dependencies = [
        ('listings', '0019_fix_favorite_table_postgres'),
    ]

    operations = [
        migrations.RunSQL(
            # SQL that marks problematic migrations as applied without running them
            sql="""
            INSERT INTO django_migrations (app, name, applied)
            VALUES
                ('listings', '0015_fix_favorite', NOW())
            ON CONFLICT DO NOTHING;
            """,
            reverse_sql="-- No reverse SQL needed"
        ),
    ] 