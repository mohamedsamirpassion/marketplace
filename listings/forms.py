from django import forms
from django.forms import inlineformset_factory
from .models import Listing, ListingImage, Brand, Model

class ListingForm(forms.ModelForm):
    brand = forms.ModelChoiceField(queryset=Brand.objects.filter(approved=True), empty_label="Select a brand")
    model = forms.ModelChoiceField(queryset=Model.objects.none(), empty_label="Select a model")

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'year', 'price', 'mileage', 'governorate', 'city', 'condition', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Brand choices: All approved brands
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
        return cleaned_data

class ListingImageForm(forms.ModelForm):
    class Meta:
        model = ListingImage
        fields = ['image']

ListingImageFormSet = inlineformset_factory(
    Listing,
    ListingImage,
    form=ListingImageForm,
    extra=10,  # Should be 10
    max_num=10,
    can_delete=False
)