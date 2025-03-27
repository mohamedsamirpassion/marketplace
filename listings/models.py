from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    approved = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('brand', 'name')

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class PendingBrand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PendingModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    year = models.IntegerField()
    price = models.IntegerField()
    mileage = models.IntegerField()
    GOVERNORATES = [
        ('Cairo', 'Cairo'),
        ('Giza', 'Giza'),
        ('Alexandria', 'Alexandria'),
        ('Greater Cairo', 'Greater Cairo'),
        ('Aswan', 'Aswan'),
        ('Asyut', 'Asyut'),
        ('Beheira', 'Beheira'),
        ('Beni Suef', 'Beni Suef'),
        ('Dakahlia', 'Dakahlia'),
        ('Damietta', 'Damietta'),
        ('Faiyum', 'Faiyum'),
        ('Gharbia', 'Gharbia'),
        ('Ismailia', 'Ismailia'),
        ('Kafr El Sheikh', 'Kafr El Sheikh'),
        ('Luxor', 'Luxor'),
        ('Matruh', 'Matruh'),
        ('Minya', 'Minya'),
        ('Monufia', 'Monufia'),
        ('New Valley', 'New Valley'),
        ('North Sinai', 'North Sinai'),
        ('Port Said', 'Port Said'),
        ('Qalyubia', 'Qalyubia'),
        ('Qena', 'Qena'),
        ('Red Sea', 'Red Sea'),
        ('Sharqia', 'Sharqia'),
        ('Sohag', 'Sohag'),
        ('South Sinai', 'South Sinai'),
        ('Suez', 'Suez'),
    ]
    governorate = models.CharField(max_length=50, choices=GOVERNORATES)  # Replaces location
    city = models.CharField(max_length=100, blank=True, null=True)  # Optional city
    condition = models.CharField(max_length=50, choices=[
        ('New', 'New'),
        ('Used', 'Used'),
        ('Damaged', 'Damaged'),
    ])
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)  # New field for rejection reason

    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

    @property
    def full_location(self):
        if self.city:
            return f"{self.governorate} - {self.city}"
        return self.governorate

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')

class AdSpace(models.Model):
    LOCATION_CHOICES = [
        ('top_banner', 'Top Banner'),
        ('sidebar', 'Sidebar'),
        ('inline', 'Inline (Every 5th Listing)'),
    ]
    location_on_page = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    ad_network_code = models.TextField()  # Stores the ad network script (e.g., AdSense/Media.net code)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"AdSpace: {self.location_on_page}"