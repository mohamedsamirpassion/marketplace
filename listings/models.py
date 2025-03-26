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
    price = models.IntegerField()  # Changed to IntegerField
    mileage = models.IntegerField()
    location = models.CharField(max_length=100)
    condition = models.CharField(max_length=50, choices=[
        ('New', 'New'),
        ('Used', 'Used'),
        ('Damaged', 'Damaged'),
    ])
    description = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  # New field for admin approval

    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')