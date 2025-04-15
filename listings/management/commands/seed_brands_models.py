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
                '3 Series', '5 Series', 'X5', 'M3', 'i4', 'X3', 'X1', '7 Series', '4 Series', 'M4', 'M5', 'X6', 'X7', 'i8', 'i3', '2 Series'
            ]),
            ('Mercedes-Benz', [
                'C-Class', 'E-Class', 'S-Class', 'GLC', 'AMG GT'
            ]),
        ]

        self.stdout.write("Starting to seed brands and models...")
        
        # First, get or create BMW brand specifically
        bmw_brand, created = Brand.objects.get_or_create(name='BMW', defaults={'approved': True})
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created brand: BMW (ID: {bmw_brand.id})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Found existing brand: BMW (ID: {bmw_brand.id})'))
            
        # Make sure BMW is approved
        if not bmw_brand.approved:
            bmw_brand.approved = True
            bmw_brand.save()
            self.stdout.write(self.style.SUCCESS(f'Updated BMW brand to approved'))
            
        # Get existing BMW models
        existing_bmw_models = list(Model.objects.filter(brand=bmw_brand).values_list('name', flat=True))
        self.stdout.write(f"Existing BMW models: {existing_bmw_models}")
        
        # Add BMW models
        for model_name in [
            '3 Series', '5 Series', 'X5', 'M3', 'i4', 'X3', 'X1', '7 Series', '4 Series', 'M4', 'M5', 'X6', 'X7', 'i8', 'i3', '2 Series'
        ]:
            model, created = Model.objects.get_or_create(
                brand=bmw_brand,
                name=model_name,
                defaults={'approved': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created model: BMW {model_name} (ID: {model.id})'))
            else:
                # Make sure it's approved
                if not model.approved:
                    model.approved = True
                    model.save()
                    self.stdout.write(self.style.SUCCESS(f'Updated BMW {model_name} to approved'))
                else:
                    self.stdout.write(f'Model already exists: BMW {model_name} (ID: {model.id})')
        
        # Now process the rest of the brands
        for brand_name, models in brands_data:
            # Skip BMW since we already processed it
            if brand_name == 'BMW':
                continue
                
            brand, created = Brand.objects.get_or_create(name=brand_name, defaults={'approved': True})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created brand: {brand_name}'))
            
            for model_name in models:
                model, created = Model.objects.get_or_create(
                    brand=brand,
                    name=model_name,
                    defaults={'approved': True}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created model: {brand_name} {model_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded brands and models'))
        
        # Output count of brands and models for verification
        brand_count = Brand.objects.count()
        model_count = Model.objects.count()
        bmw_model_count = Model.objects.filter(brand__name='BMW').count()
        
        self.stdout.write(f"Database now has {brand_count} brands and {model_count} models")
        self.stdout.write(f"BMW has {bmw_model_count} models")