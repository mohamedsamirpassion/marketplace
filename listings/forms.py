from django import forms
from django.forms import inlineformset_factory
from .models import Listing, ListingImage, Brand, Model, PendingBrand, PendingModel

class ListingForm(forms.ModelForm):
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(approved=True),
        empty_label="Select a brand",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    model = forms.ModelChoiceField(
        queryset=Model.objects.none(),
        empty_label="Select a model",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Listing
        fields = ['brand', 'model', 'year', 'price', 'mileage', 'governorate', 'city', 'condition', 'transmission', 'fuel_type', 'description']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control'}),
            'governorate': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'transmission': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
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
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control d-none', 'accept': 'image/*'}),
        }

ListingImageFormSet = inlineformset_factory(
    Listing,
    ListingImage,
    form=ListingImageForm,
    extra=10,
    max_num=10,
    can_delete=False
)

class PendingBrandForm(forms.ModelForm):
    class Meta:
        model = PendingBrand
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PendingModelForm(forms.ModelForm):
    class Meta:
        model = PendingModel
        fields = ['brand', 'name']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['brand'].queryset = Brand.objects.filter(approved=True)
        self.fields['brand'].label_from_instance = lambda obj: obj.name