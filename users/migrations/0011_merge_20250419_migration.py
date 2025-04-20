from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is created to merge the two separate branches of the migration history.
    """
    
    dependencies = [
        ('users', '0003_user_country_code_user_has_whatsapp'),
        ('users', '0010_fix_postgresql_autoincrement'),
    ]

    operations = [
        # No operations needed, this just merges the branches
    ] 