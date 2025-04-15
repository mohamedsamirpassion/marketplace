from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import urllib.parse

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, name, password=None):
        if not email:
            raise ValueError("Email is required")
        if not phone_number:
            raise ValueError("Phone number is required")
        if not name:
            raise ValueError("Name is required")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, name, password=None):
        user = self.create_user(email, phone_number, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    country_code = models.CharField(max_length=5, default='+20')  # Default to Egypt (+20)
    phone_number = models.CharField(max_length=15, unique=True)
    has_whatsapp = models.BooleanField(default=True)  # Default to True as WhatsApp is common
    name = models.CharField(max_length=100)  # New field
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'name']

    def __str__(self):
        return self.name  # Show name instead of email

    def get_full_phone_number(self):
        """Return the full phone number with country code"""
        return f"{self.country_code}{self.phone_number}"

    def get_whatsapp_link(self, listing=None):
        """Generate WhatsApp API link if the user has WhatsApp
        
        If listing is provided, include a message about the listing.
        """
        if self.has_whatsapp:
            # Remove any spaces or special characters from the phone number
            clean_number = self.get_full_phone_number().replace(' ', '').replace('-', '').replace('+', '')
            
            if listing:
                # Create a message that includes the listing details and URL
                listing_url = f"http://127.0.0.1:8000/listing/{listing.id}/"
                message = f"Hi, I'm interested in your {listing.brand.name} {listing.model.name} ({listing.year}) listed on Cairo Bazaar: {listing_url}"
                
                # URL encode the message
                encoded_message = urllib.parse.quote(message)
                
                return f"https://wa.me/{clean_number}?text={encoded_message}"
            
            return f"https://wa.me/{clean_number}"
        return None