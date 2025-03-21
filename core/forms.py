from django import forms
from .models import Car

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['title', 'brand', 'price', 'location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }