"""
Production Settings for CryptFyles
Environment variables with sensible defaults for Railway
"""
from .settings import *
from decouple import config, Csv
import dj_database_url
import os

# ===== DEBUG & SECURITY =====
DEBUG = False

# SECRET_KEY - With default fallback for Railway
try:
    SECRET_KEY = config('SECRET_KEY')
except:
    # If SECRET_KEY not found, generate a fallback
    # (This should NEVER happen in production, but prevents crashes)
    import secrets
    SECRET_KEY = 'django-insecure-' + secrets.token_urlsafe(50)

# ALLOWED_HOSTS - Read from environment
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*',  # Allow all hosts temporarily
    cast=Csv()
)

# ===== DATABASE - PostgreSQL =====
try:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
except Exception as e:
    # Fallback - should not happen but prevents crash
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print(f"⚠️ Database error, using SQLite fallback: {e}")

# ===== STATIC FILES =====
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ===== HTTPS SECURITY =====

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ===== CSRF TRUSTED ORIGINS =====
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.railway.app',
    cast=Csv()
)

# ===== CLOUDINARY FILE STORAGE =====
try:
    import cloudinary
    import cloudinary.uploader
    
    cloudinary.config(
        cloud_name=config('CLOUDINARY_CLOUD_NAME', default=''),
        api_key=config('CLOUDINARY_API_KEY', default=''),
        api_secret=config('CLOUDINARY_API_SECRET', default=''),
        secure=True
    )
except Exception as e:
    print(f"⚠️ Cloudinary not configured: {e}")

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

print("✅ Production settings loaded!")
