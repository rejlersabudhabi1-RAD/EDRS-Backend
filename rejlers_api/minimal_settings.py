"""
MINIMAL Railway settings - removes all complexity
"""
import os
import dj_database_url
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-railway-temp-key-replace-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Minimal allowed hosts
ALLOWED_HOSTS = ['*']  # Allow all hosts for Railway

# Application definition - MINIMAL
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'rejlers_api.minimal_urls'

WSGI_APPLICATION = 'rejlers_api.minimal_wsgi.application'

# Database - Railway PostgreSQL
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# CORS - Allow all origins for now
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'