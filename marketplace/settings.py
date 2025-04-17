"""
Django settings for marketplace project.

Generated by 'django-admin startproject' using Django 4.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, skip loading

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'users.User'  # Tell Django to use our custom model

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-dev-key-for-local-use-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Add railway and render domains
if not DEBUG:
    ALLOWED_HOSTS.extend([
        '.up.railway.app',
        '.onrender.com',
        '.cairobazaar.com',  # For future domain
        'cairo-bazaar.onrender.com'  # Added for Render domain
    ])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required for allauth
    
    # Django Allauth - core
    'allauth',
    'allauth.account',
    # Social providers
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    # 'allauth.socialaccount.providers.facebook',
    
    'widget_tweaks',
    'crispy_forms',  # Add crispy_forms
    'crispy_bootstrap4',  # Add crispy_bootstrap4
    'users.apps.UsersConfig',
    'listings.apps.ListingsConfig',
    'core.apps.CoreConfig',  # Add the core app
    'contact.apps.ContactConfig',  # Add the contact app
    'storages',  # Add django-storages
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line for static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Must come before our custom middleware
    # 'django.middleware.locale.LocaleMiddleware',  # Comment out the default locale middleware
    'core.middleware.CustomLocaleMiddleware',  # Add our custom middleware
    'users.middleware.RefreshUserMiddleware',  # Add our user refresh middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Add allauth middleware
]

ROOT_URLCONF = 'marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'listings.admin.listings_admin_context_processor',
                'core.context_processors.language_context_processor',
                'users.context_processors.current_user_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'marketplace.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Languages available for the site
LANGUAGES = [
    ('en', 'English'),
    ('ar', 'العربية'),  # Arabic
]

# Where Django should look for translation files
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Language cookie settings
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 year

# For right-to-left languages like Arabic
USE_L10N = True

# Add this setting to use English as a fallback when translations are missing
LANGUAGE_CODE = 'en-us'
# This setting will make Django use English strings if a translation is missing
USE_I18N = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'  # Redirect to homepage after login
LOGOUT_REDIRECT_URL = '/'  # Redirect to homepage after logout

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email Configuration
if DEBUG:
    # Use console backend for development
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Use SMTP backend for production
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

DEFAULT_FROM_EMAIL = 'noreply@cairobazaar.com'

# Site URL for absolute URLs in emails and admin functions
# Get from environment variable if available, otherwise use defaults
SITE_URL = os.environ.get('SITE_URL', 'http://127.0.0.1:8000' if DEBUG else 'https://cairo-bazaar.onrender.com')

# Django Allauth settings
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1  # Required for allauth

# Updated Allauth settings
ACCOUNT_LOGIN_METHODS = ['email']  # New setting replacing ACCOUNT_AUTHENTICATION_METHOD
ACCOUNT_SIGNUP_FIELDS = ['email*']  # Modified to include 'email*' for mandatory verification

# Remove deprecated settings
# ACCOUNT_AUTHENTICATION_METHOD = 'email'  # Deprecated
# ACCOUNT_EMAIL_REQUIRED = True  # Deprecated 
# ACCOUNT_USERNAME_REQUIRED = False  # Deprecated

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True

# Disable social accounts for now
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID', ''),
            'secret': os.environ.get('GOOGLE_CLIENT_SECRET', ''),
            'key': ''  # Not needed for Google
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

# Social account settings
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_AUTO_SIGNUP = True  # Auto signup if user logs in via social
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'  # No additional verification for social accounts

# Use our custom signup form
ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSignupForm',
}

# Use our custom adapters
ACCOUNT_ADAPTER = 'users.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

# Explicitly tell allauth to use email as the username field
ACCOUNT_USER_MODEL_USERNAME_FIELD = None  # Our User model doesn't have a username field

# Login/logout URLs
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Add default settings for language cookie
LANGUAGE_COOKIE_PATH = '/'
LANGUAGE_COOKIE_DOMAIN = None
LANGUAGE_COOKIE_SECURE = False
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = None

# Session settings to ensure user data is preserved
SESSION_SAVE_EVERY_REQUEST = True  # Save the session data on every request
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Use database-backed sessions

# Add at the end of file, after all other settings
# Configure static files for production
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configure database for production
import dj_database_url
if not DEBUG:
    # Parse database URL without forcing SSL
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=False)
    }
    
# Configure HTTPS settings for production
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Crispy Forms Settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap4"
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Logging configuration to debug Allauth
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'allauth': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# AWS S3 Storage Settings (Production Only)
if not DEBUG:
    # Credentials and Bucket Info from Environment Variables
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME') # e.g., 'eu-north-1'

    if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME]):
        # Storage Backend
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

        # Optional: If you want files to be stored in a 'media/' subfolder within the bucket
        AWS_LOCATION = 'media' 

        # Generate Media URL
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'

        # S3 Settings
        AWS_DEFAULT_ACL = 'public-read' # Make files publicly readable by default
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400', # Cache files for 1 day
        }
        AWS_QUERYSTRING_AUTH = False # Do not add authentication parameters to URLs
        AWS_HEADERS = { # Add Cache-Control header to uploads
            'Cache-Control': 'max-age=86400',
        }
    else:
        print("Warning: S3 storage credentials not fully configured. Media files might not work correctly in production.")
# END AWS S3 Storage Settings