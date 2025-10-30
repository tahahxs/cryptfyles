"""
Production Settings for CryptFyles
This file is used when deployed to Railway
"""
from .settings import *
from decouple import config, Csv
import dj_database_url
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Import SECRET_KEY from environment variable
SECRET_KEY = config('SECRET_KEY')

# Allowed hosts (Railway domains)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# Database Configuration (PostgreSQL from Railway)
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,  # Keep connections alive for 10 minutes
        conn_health_checks=True,  # Check connection before each request
    )
}

# Static Files Configuration
# WhiteNoise serves static files (CSS/JS) efficiently
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# HTTPS Security Settings
SECURE_SSL_REDIRECT = True  # Force HTTPS
SESSION_COOKIE_SECURE = True  # Cookies only over HTTPS
CSRF_COOKIE_SECURE = True  # CSRF tokens only over HTTPS
SECURE_BROWSER_XSS_FILTER = True  # Browser XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME sniffing
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_HSTS_SECONDS = 31536000  # HSTS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', cast=Csv())

# Cloudinary Configuration for File Storage
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
    secure=True
)

# File Upload Settings
DATA_UPLOAD_MAX_MEMORY_SIZE = 10737418240  # 10GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10737418240  # 10GB

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
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

print("✅ Production settings loaded successfully! - Redeployed")
