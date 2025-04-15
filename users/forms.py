from django import forms
from .models import User
import re
from django.contrib.auth import get_user_model
from allauth.account.forms import LoginForm, SignupForm

User = get_user_model()

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    phone_number = forms.CharField(label="Phone Number (without country code)")
    
    COUNTRY_CHOICES = [
        ('+20', '🇪🇬 Egypt (+20)'),
        ('+1', '🇺🇸 United States (+1)'),
        ('+44', '🇬🇧 United Kingdom (+44)'),
        ('+966', '🇸🇦 Saudi Arabia (+966)'),
        ('+971', '🇦🇪 United Arab Emirates (+971)'),
        ('+974', '🇶🇦 Qatar (+974)'),
        ('+965', '🇰🇼 Kuwait (+965)'),
        ('+962', '🇯🇴 Jordan (+962)'),
        ('+961', '🇱🇧 Lebanon (+961)'),
        ('+963', '🇸🇾 Syria (+963)'),
    ]
    
    country_code = forms.ChoiceField(choices=COUNTRY_CHOICES, initial='+20', label="Country Code")
    has_whatsapp = forms.BooleanField(required=False, initial=True, label="This number has WhatsApp")

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'country_code', 'has_whatsapp']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        country_code = self.cleaned_data.get('country_code', '+20')
        
        # Remove any non-numeric characters
        phone_number = re.sub(r'\D', '', phone_number)
        
        # For Egypt numbers, handle the leading zero
        if country_code == '+20' and phone_number.startswith('0'):
            phone_number = phone_number[1:]  # Remove the leading zero
            
        # Check the length based on country code
        if country_code == '+20' and len(phone_number) != 10:
            raise forms.ValidationError("Egyptian phone numbers should be 10 digits (or 9 digits if you exclude the leading zero).")
            
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """Custom form for editing user profile"""
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="New Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=False, label="Confirm New Password")
    
    COUNTRY_CHOICES = [
        ('+20', '🇪🇬 Egypt (+20)'),
        ('+1', '🇺🇸 United States (+1)'),
        ('+44', '🇬🇧 United Kingdom (+44)'),
        ('+966', '🇸🇦 Saudi Arabia (+966)'),
        ('+971', '🇦🇪 United Arab Emirates (+971)'),
        ('+974', '🇶🇦 Qatar (+974)'),
        ('+965', '🇰🇼 Kuwait (+965)'),
        ('+962', '🇯🇴 Jordan (+962)'),
        ('+961', '🇱🇧 Lebanon (+961)'),
        ('+963', '🇸🇾 Syria (+963)'),
    ]
    
    country_code = forms.ChoiceField(choices=COUNTRY_CHOICES, label="Country Code")
    has_whatsapp = forms.BooleanField(required=False, label="This number has WhatsApp")

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'country_code', 'has_whatsapp']
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
            
        return cleaned_data

class CustomSignupForm(SignupForm):
    """Custom signup form that includes the name field"""
    name = forms.CharField(max_length=100, label='Full Name', 
                          widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    
    def save(self, request):
        user = super().save(request)
        user.name = self.cleaned_data['name']
        user.save()
        return user