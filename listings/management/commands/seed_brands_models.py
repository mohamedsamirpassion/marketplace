from django.core.management.base import BaseCommand
from listings.models import Brand, Model

class Command(BaseCommand):
    help = 'Seeds the database with initial brands and models'

    def handle(self, *args, **kwargs):
        # Prebuilt brands
        brands_data = [
            ('Toyota', [
                'Camry', 'Corolla', 'RAV4', 'Prius', 'Highlander'
            ]),
            ('Honda', [
                'Civic', 'Accord', 'CR-V', 'Pilot', 'Fit'
            ]),
            ('Ford', [
                'Mustang', 'F-150', 'Explorer', 'Focus', 'Escape'
            ]),
            ('BMW', [
                '3 Series', '5 Series', 'X5', 'M3', 'i4'
            ]),
            ('Mercedes-Benz', [
                'C-Class', 'E-Class', 'S-Class', 'GLC', 'AMG GT'
            ]),
        ]

        for brand_name, models in brands_data:
            brand, created = Brand.objects.get_or_create(name=brand_name, approved=True)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created brand: {brand_name}'))
            for model_name in models:
                Model.objects.get_or_create(brand=brand, name=model_name, approved=True)
                self.stdout.write(self.style.SUCCESS(f'Created model: {brand_name} {model_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded brands and models'))