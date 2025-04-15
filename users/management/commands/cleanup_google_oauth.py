from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Cleans up duplicate Google OAuth apps and creates a single valid one'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', required=True, help='Google OAuth Client ID')
        parser.add_argument('--secret', required=True, help='Google OAuth Secret Key')

    def handle(self, *args, **options):
        client_id = options['client_id']
        secret = options['secret']

        # Get the current site
        site = Site.objects.get_current()
        
        # Delete all existing Google apps
        google_apps = SocialApp.objects.filter(provider='google')
        count = google_apps.count()
        
        if count > 0:
            self.stdout.write(self.style.WARNING(f'Found {count} Google OAuth apps. Deleting all...'))
            google_apps.delete()
        
        # Create a new Google app
        self.stdout.write(self.style.SUCCESS('Creating new Google OAuth app...'))
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=secret
        )
        
        # Associate with the current site
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully set up Google OAuth for site {site.domain}'))
        self.stdout.write(self.style.SUCCESS('Client ID: ' + client_id))
        self.stdout.write(self.style.SUCCESS('Secret: ' + '*' * len(secret))) 