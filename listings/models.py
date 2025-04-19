from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import cloudinary
import cloudinary.uploader
from cloudinary.models import CloudinaryField

User = get_user_model()

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Arabic Name"))
    approved = models.BooleanField(default=True)

    def __str__(self):
        from django.utils.translation import get_language
        if get_language() == 'ar' and self.name_ar:
            return self.name_ar
        return self.name

class Model(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Arabic Name"))
    approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('brand', 'name')

    def __str__(self):
        from django.utils.translation import get_language
        if get_language() == 'ar' and self.name_ar:
            brand_name = self.brand.name_ar if self.brand.name_ar else self.brand.name
            return f"{brand_name} {self.name_ar}"
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
        ('Cairo', _('Cairo')),
        ('Giza', _('Giza')),
        ('Alexandria', _('Alexandria')),
        ('Greater Cairo', _('Greater Cairo')),
        ('Aswan', _('Aswan')),
        ('Asyut', _('Asyut')),
        ('Beheira', _('Beheira')),
        ('Beni Suef', _('Beni Suef')),
        ('Dakahlia', _('Dakahlia')),
        ('Damietta', _('Damietta')),
        ('Faiyum', _('Faiyum')),
        ('Gharbia', _('Gharbia')),
        ('Ismailia', _('Ismailia')),
        ('Kafr El Sheikh', _('Kafr El Sheikh')),
        ('Luxor', _('Luxor')),
        ('Matruh', _('Matruh')),
        ('Minya', _('Minya')),
        ('Monufia', _('Monufia')),
        ('New Valley', _('New Valley')),
        ('North Sinai', _('North Sinai')),
        ('Port Said', _('Port Said')),
        ('Qalyubia', _('Qalyubia')),
        ('Qena', _('Qena')),
        ('Red Sea', _('Red Sea')),
        ('Sharqia', _('Sharqia')),
        ('Sohag', _('Sohag')),
        ('South Sinai', _('South Sinai')),
        ('Suez', _('Suez')),
    ]
    governorate = models.CharField(max_length=50, choices=GOVERNORATES)  # Replaces location
    city = models.CharField(max_length=100, blank=True, null=True)  # Optional city
    condition = models.CharField(max_length=50, choices=[
        ('New', _('New')),
        ('Used', _('Used')),
        ('Damaged', _('Damaged')),
    ])
    TRANSMISSION_CHOICES = [
        ('Automatic', _('Automatic')),
        ('Manual', _('Manual')),
    ]
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    FUEL_TYPE_CHOICES = [
        ('Gas', _('Petrol')),
        ('Diesel', _('Diesel')),
        ('Electric', _('Electric')),
        ('Hybrid', _('Hybrid')),
        ('Natural Gas', _('Natural Gas')),
    ]
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='Gas')  # New field
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True, null=True)  # New field for rejection reason
    is_sold = models.BooleanField(default=False)  # Track if the listing has been sold
    sold_date = models.DateTimeField(blank=True, null=True)  # Date when the item was marked as sold
    has_multiple_reports = models.BooleanField(default=False)  # Flag for listings with multiple reports

    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

    @property
    def full_location(self):
        if self.city:
            return f"{self.governorate} - {self.city}"
        return self.governorate

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')
    
    def get_url(self):
        return self.image.url

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

class ListingReport(models.Model):
    REPORT_REASONS = (
        ('spam', _('Spam or Misleading')),
        ('fraud', _('Fraudulent Listing')),
        ('offensive', _('Offensive Content')),
        ('wrong_info', _('Incorrect Information')),
        ('fake_images', _('Fake Images')),
        ('other', _('Other')),
    )
    STATUS_CHOICES = (
        ('pending', _('Pending Review')),
        ('resolved', _('Resolved')),
        ('dismissed', _('Dismissed')),
    )
    
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_listings')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_note = models.TextField(blank=True)
    reported_on = models.DateTimeField(default=timezone.now)
    resolved_on = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report on {self.listing} - {self.get_reason_display()}"
    
    def resolve(self, note=None):
        self.status = 'resolved'
        if note:
            self.admin_note = note
        self.resolved_on = timezone.now()
        self.save()
    
    def dismiss(self, note=None):
        self.status = 'dismissed'
        if note:
            self.admin_note = note
        self.resolved_on = timezone.now()
        self.save()

class Favorite(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
        
    def __str__(self):
        return f"{self.user.name} - {self.listing}"