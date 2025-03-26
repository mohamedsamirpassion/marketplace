from django.db import models
from users.models import User

class CarListing(models.Model):
    title = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField()
    category = models.CharField(max_length=50, default="Cars")
    condition = models.CharField(max_length=20, choices=[('new', 'New'), ('used', 'Used')])
    year = models.IntegerField()
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    mileage = models.IntegerField()
    location = models.CharField(max_length=100)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )

    def __str__(self):
        return f"{self.make} {self.model} - {self.title}"

class CarImage(models.Model):
    car_listing = models.ForeignKey(CarListing, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='car_images/')