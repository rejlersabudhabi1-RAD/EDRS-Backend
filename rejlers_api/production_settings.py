"""
Production settings for Railway deployment
Inherits from base settings and overrides for production environment
"""

import os
import dj_database_url
from .settings import *

# Security Settings for Production
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Handle SECRET_KEY with fallback
SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    # Generate a temporary secret key for initial deployment
    import secrets
    SECRET_KEY = secrets.token_urlsafe(50)
    print("WARNING: Using generated SECRET_KEY. Set DJANGO_SECRET_KEY environment variable.")

# Railway-compatible ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*.railway.app',
    '*.up.railway.app',
    '.railway.app',
    '.up.railway.app',
]

# Add custom hosts from environment
if os.environ.get('ALLOWED_HOSTS'):
    ALLOWED_HOSTS.extend(os.environ.get('ALLOWED_HOSTS').split(','))

# Add Railway URLs
if os.environ.get('RAILWAY_STATIC_URL'):
    railway_host = os.environ.get('RAILWAY_STATIC_URL').replace('https://', '').replace('http://', '')
    if railway_host:
        ALLOWED_HOSTS.append(railway_host)

# Database Configuration for Railway
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Fallback to PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('PGDATABASE', 'rejlers_db'),
            'USER': os.environ.get('PGUSER', 'rejlers_user'),
            'PASSWORD': os.environ.get('PGPASSWORD', ''),
            'HOST': os.environ.get('PGHOST', 'localhost'),
            'PORT': os.environ.get('PGPORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }

# Static Files Configuration for Railway
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files (use cloud storage in production)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security Headers - Relaxed for Railway initial deployment
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 0  # Disabled initially for Railway
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Less restrictive for Railway

# CORS Settings for Production
CORS_ALLOWED_ORIGINS = [
    "https://rejlers-edrs.vercel.app",  # Add your frontend domain
    "https://edrs.rejlers.ae",         # Add your custom domain if any
    os.environ.get('FRONTEND_URL', 'http://localhost:3000'),
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

# Cache Configuration with Redis
if 'REDIS_URL' in os.environ:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email Configuration (use environment variables)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@rejlers.ae')

# JWT Settings
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
})

# OpenAI API Key (for AI features)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# AWS Configuration (if using AWS services)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

print("✅ Production settings loaded for Railway deployment")