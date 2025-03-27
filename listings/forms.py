from django import forms
from django.forms import modelformset_factory
from .models import Listing, ListingImage, Brand, Model

class ListingForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=Brand.objects.filter(approved=True), empty_label="Select a brand")
    model = forms.ModelChoiceField(queryset=Model.objects.none(), empty_label="Select a model")
    new_brand = forms.CharField(max_length=100, required=False, label="New Brand (if not in list)", widget=forms.HiddenInput())
    new_model = forms.CharField(max_length=100, required=False, label="New Model (if not in list)", widget=forms.HiddenInput())

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'year', 'price', 'mileage', 'governorate', 'city', 'condition', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Brand choices: All approved brands, no "Other"
        self.fields['brand'].queryset = Brand.objects.filter(approved=True)
        self.fields['brand'].choices = [(None, 'Select a brand')] + [(brand.id, brand.name) for brand in Brand.objects.filter(approved=True)]
        
        # Model choices: Update based on selected brand
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Model.objects.filter(brand_id=brand_id, approved=True)
                self.fields['model'].choices = [(None, 'Select a model')] + [(model.id, model.name) for model in Model.objects.filter(brand_id=brand_id, approved=True)]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.brand:
            self.fields['model'].queryset = Model.objects.filter(brand=self.instance.brand, approved=True)
            self.fields['model'].choices = [(None, 'Select a model')] + [(model.id, model.name) for model in Model.objects.filter(brand=self.instance.brand, approved=True)]

    def clean(self):
        cleaned_data = super().clean()
        # Remove "Other" logic since we’re not using it anymore
        return cleaned_data

ListingImageFormSet = modelformset_factory(ListingImage, fields=('image',), extra=10, max_num=10)