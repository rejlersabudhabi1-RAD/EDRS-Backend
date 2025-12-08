"""
Django settings for Rejlers API system.

Advanced and secure API backend for Rejlers engineering consultancy.
Developed with modern Django practices and security measures.
"""

from pathlib import Path
from decouple import config
from datetime import timedelta
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security Configuration
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')


# Application definition

INSTALLED_APPS = [
    # Django Core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party packages
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Rejlers Apps
    'authentication',
    'projects',
    'services',
    'team',
    
    # AI-Powered ERP Apps
    'ai_erp',
    'drawing_analysis',
    'simulation_management',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rejlers_api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rejlers_api.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'OtUKsnrCAhrRCCFbAjKLWVnilkdsUhHR',
        'HOST': 'ballast.proxy.rlwy.net',
        'PORT': '49545',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'authentication.RejlersUser'

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'authentication.backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('JWT_SECRET_KEY', default=SECRET_KEY),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS Configuration for Frontend Integration
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development

# API Configuration
API_VERSION = config('API_VERSION', default='v1')
API_TITLE = config('API_TITLE', default='Rejlers API System')
API_DESCRIPTION = config('API_DESCRIPTION', default='Advanced API system for Rejlers engineering consultancy')

# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = config('MAX_UPLOAD_SIZE', default='10485760', cast=int)  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = FILE_UPLOAD_MAX_MEMORY_SIZE

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'rejlers_api.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
        'rejlers_api': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# AI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4o-mini'
OPENAI_VISION_MODEL = 'gpt-4o-mini'
OPENAI_MAX_TOKENS = 4000
OPENAI_TEMPERATURE = 0.7

# AI ERP Configuration
AI_ERP_DRAWING_ANALYSIS = {
    'SUPPORTED_FORMATS': ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'dwg', 'dxf'],
    'MAX_FILE_SIZE': 50 * 1024 * 1024,  # 50MB
    'ANALYSIS_TIMEOUT': 300,  # 5 minutes
}

# Oil & Gas Engineering Domains
ENGINEERING_DOMAINS = {
    'UPSTREAM': ['Drilling', 'Production', 'Reservoir', 'Geophysics'],
    'MIDSTREAM': ['Pipeline', 'Transportation', 'Storage', 'Processing'],
    'DOWNSTREAM': ['Refining', 'Petrochemicals', 'Distribution', 'Marketing'],
    'OFFSHORE': ['Platform Design', 'Subsea', 'Marine', 'FPSO'],
    'ONSHORE': ['Facilities', 'Infrastructure', 'Process', 'Utilities'],
}

# Role-Based Access Control
RBAC_ROLES = {
    'SUPER_ADMIN': {
        'permissions': ['*'],
        'redirect_url': '/admin/dashboard/',
        'description': 'Full system access and control'
    },
    'PROJECT_MANAGER': {
        'permissions': ['project.*', 'drawing.read', 'simulation.read', 'team.read'],
        'redirect_url': '/pm/dashboard/',
        'description': 'Project management and oversight'
    },
    'SENIOR_ENGINEER': {
        'permissions': ['drawing.*', 'simulation.*', 'analysis.create'],
        'redirect_url': '/engineer/dashboard/',
        'description': 'Full engineering capabilities'
    },
    'ENGINEER': {
        'permissions': ['drawing.read', 'drawing.analyze', 'simulation.read'],
        'redirect_url': '/engineer/workspace/',
        'description': 'Standard engineering access'
    },
    'ANALYST': {
        'permissions': ['drawing.read', 'analysis.read', 'reports.generate'],
        'redirect_url': '/analyst/dashboard/',
        'description': 'Analysis and reporting access'
    },
    'VIEWER': {
        'permissions': ['*.read'],
        'redirect_url': '/viewer/dashboard/',
        'description': 'Read-only access to approved content'
    }
}

# =============================================================================
# AWS CONFIGURATION
# =============================================================================

# AWS Credentials and Region
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = config('AWS_DEFAULT_REGION', default='eu-north-1')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-north-1')

# AWS S3 Storage Configuration
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='rejlers-edrs-project')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_S3_FILE_OVERWRITE = config('AWS_S3_FILE_OVERWRITE', default=False, cast=bool)
AWS_DEFAULT_ACL = config('AWS_DEFAULT_ACL', default='private')
AWS_S3_VERIFY = config('AWS_S3_VERIFY', default=True, cast=bool)
AWS_S3_USE_SSL = config('AWS_S3_USE_SSL', default=True, cast=bool)

# Static and Media Files Storage (using S3)
if not DEBUG:
    # Production: Use S3 for static and media files
    AWS_LOCATION = 'static'
    AWS_MEDIA_LOCATION = 'media'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_LOCATION}/'
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_MEDIA_LOCATION}/'

# =============================================================================
# EMAIL CONFIGURATION (AWS SES)
# =============================================================================

# AWS SES Configuration
AWS_SES_REGION_NAME = config('AWS_SES_REGION_NAME', default='eu-north-1')
AWS_SES_ACCESS_KEY_ID = config('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = config('AWS_SES_SECRET_ACCESS_KEY')

# Email Backend Configuration
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='email-smtp.eu-north-1.amazonaws.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)

# Default email addresses
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@rejlers.com')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@rejlers.com')

# Email settings for user notifications
ADMINS = [('Admin', 'admin@rejlers.com')]
MANAGERS = ADMINS

# =============================================================================
# AWS LOGGING (CloudWatch) - Optional
# =============================================================================

AWS_CLOUDWATCH_LOG_GROUP = config('AWS_CLOUDWATCH_LOG_GROUP', default='rejlers-erp-logs')
AWS_CLOUDWATCH_LOG_STREAM = config('AWS_CLOUDWATCH_LOG_STREAM', default='django-app')

# Add CloudWatch handler to logging if in production
if not DEBUG:
    LOGGING['handlers']['cloudwatch'] = {
        'level': 'INFO',
        'class': 'watchtower.CloudWatchLogHandler',
        'log_group': AWS_CLOUDWATCH_LOG_GROUP,
        'stream_name': AWS_CLOUDWATCH_LOG_STREAM,
        'boto3_session': None,  # Will use default credentials
    }
    LOGGING['root']['handlers'].append('cloudwatch')
