from django import forms
from django.forms import inlineformset_factory
from .models import CarListing, CarImage

class CarListingForm(forms.ModelForm):
    class Meta:
        model = CarListing
        fields = [
            'title', 'price', 'description', 'condition', 'year',
            'make', 'model', 'mileage', 'location'
        ]
        widgets = {
            'condition': forms.Select(choices=[('new', 'New'), ('used', 'Used')]),
        }

CarImageFormSet = inlineformset_factory(
    CarListing, CarImage, fields=['image'], extra=10, max_num=10
)