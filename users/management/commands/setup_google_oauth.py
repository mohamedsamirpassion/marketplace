from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

class Command(BaseCommand):
    help = 'Sets up the Google OAuth provider for django-allauth'

    def add_arguments(self, parser):
        parser.add_argument('--client_id', required=True, help='Google OAuth Client ID')
        parser.add_argument('--secret', required=True, help='Google OAuth Secret Key')

    def handle(self, *args, **options):
        client_id = options['client_id']
        secret = options['secret']

        # Get the current site
        site = Site.objects.get_current()
        
        # Check if a Google app already exists
        google_app = SocialApp.objects.filter(provider='google').first()
        
        if google_app:
            self.stdout.write(self.style.WARNING('Google OAuth app already exists. Updating...'))
            google_app.client_id = client_id
            google_app.secret = secret
            google_app.save()
        else:
            self.stdout.write(self.style.SUCCESS('Creating new Google OAuth app...'))
            google_app = SocialApp.objects.create(
                provider='google',
                name='Google',
                client_id=client_id,
                secret=secret
            )
        
        # Make sure the app is associated with the current site
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully set up Google OAuth for site {site.domain}'))
        self.stdout.write(self.style.SUCCESS('Client ID: ' + client_id))
        self.stdout.write(self.style.SUCCESS('Secret: ' + '*' * len(secret))) 