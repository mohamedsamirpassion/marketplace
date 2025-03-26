from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

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
    phone_number = models.CharField(max_length=15, unique=True)
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