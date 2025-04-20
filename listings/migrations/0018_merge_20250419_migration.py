from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration is created to merge the two separate branches of the migration history.
    """
    
    dependencies = [
        ('listings', '0016_fix_postgresql_autoincrement'),
        ('listings', '0017_alter_listingimage_image'),
    ]

    operations = [
        # No operations needed, this just merges the branches
    ] 