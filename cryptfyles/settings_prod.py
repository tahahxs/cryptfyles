"""
Production Settings for CryptFyles
This file loads all configuration from environment variables
"""
from .settings import *
from decouple import config, Csv
import dj_database_url
import os

# ===== DEBUG & SECURITY =====
DEBUG = False

# SECRET_KEY - MUST come from Railway environment variable
SECRET_KEY = config('SECRET_KEY')

# ALLOWED_HOSTS - Read from environment with fallback
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*.railway.app,localhost,127.0.0.1',
    cast=Csv()
)

# ===== DATABASE - PostgreSQL =====
# Railway provides DATABASE_URL automatically
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# ===== STATIC FILES =====
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ===== HTTPS SECURITY =====
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ===== CSRF TRUSTED ORIGINS =====
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app',
    cast=Csv()
)

# ===== CLOUDINARY FILE STORAGE =====
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=config('CLOUDINARY_CLOUD_NAME'),
    api_key=config('CLOUDINARY_API_KEY'),
    api_secret=config('CLOUDINARY_API_SECRET'),
    secure=True
)

# ===== LOGGING =====
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print("✅ Production settings loaded successfully from environment variables!")
