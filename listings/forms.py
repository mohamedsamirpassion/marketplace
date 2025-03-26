from django import forms
from django.forms import modelformset_factory
from .models import Listing, ListingImage, Brand, Model, PendingBrand, PendingModel

class ListingForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=Brand.objects.filter(approved=True), empty_label="Select a brand")
    model = forms.ModelChoiceField(queryset=Model.objects.none(), empty_label="Select a model")  # Will be populated dynamically
    new_brand = forms.CharField(max_length=100, required=False, label="New Brand (if not in list)")
    new_model = forms.CharField(max_length=100, required=False, label="New Model (if not in list)")

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'year', 'price', 'mileage', 'location', 'condition', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add "Other" option to brand dropdown
        self.fields['brand'].choices = [(None, 'Select a brand')] + [(brand.id, brand.name) for brand in Brand.objects.filter(approved=True)] + [('other', 'Other')]
        # Dynamically update model choices based on selected brand
        if 'brand' in self.data:
            try:
                brand_id = int(self.data.get('brand'))
                self.fields['model'].queryset = Model.objects.filter(brand_id=brand_id, approved=True)
                self.fields['model'].choices = [(None, 'Select a model')] + [(model.id, model.name) for model in Model.objects.filter(brand_id=brand_id, approved=True)] + [('other', 'Other')]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.brand:
            self.fields['model'].queryset = Model.objects.filter(brand=self.instance.brand, approved=True)
            self.fields['model'].choices = [(None, 'Select a model')] + [(model.id, model.name) for model in Model.objects.filter(brand=self.instance.brand, approved=True)] + [('other', 'Other')]

    def clean(self):
        cleaned_data = super().clean()
        brand = cleaned_data.get('brand')
        model = cleaned_data.get('model')
        new_brand = cleaned_data.get('new_brand')
        new_model = cleaned_data.get('new_model')

        # Handle "Other" brand
        if str(brand) == 'other':
            if not new_brand:
                self.add_error('new_brand', 'Please specify the new brand.')
            else:
                cleaned_data['brand'] = new_brand  # Will be handled in the view
        # Handle "Other" model
        if str(model) == 'other':
            if not new_model:
                self.add_error('new_model', 'Please specify the new model.')
            else:
                cleaned_data['model'] = new_model  # Will be handled in the view

        return cleaned_data

ListingImageFormSet = modelformset_factory(ListingImage, fields=('image',), extra=10, max_num=10)