"""
Production Settings for CryptFyles
"""
from .settings import *
from decouple import config, Csv
import dj_database_url
import os

# SECURITY SETTINGS
DEBUG = False

# SECRET_KEY with fallback
try:
    SECRET_KEY = config('z5fo8v)-opewmey@9p4-(#npy+4-0_ynz$dkt!g9h$3qyh@&3+')
except:
    SECRET_KEY = 'z5fo8v)-opewmey@9p4-(#npy+4-0_ynz$dkt!g9h$3qyh@&3+'

# ALLOWED HOSTS - WILDCARD FOR NOW

# ALLOWED_HOSTS - Read from environment with fallback
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*.railway.app,localhost,127.0.0.1',
    cast=Csv()
)

# DATABASE
try:
    DATABASES = {
        'default': dj_database_url.config(
            default=config('postgresql://${{PGUSER}}:${{POSTGRES_PASSWORD}}@${{RAILWAY_PRIVATE_DOMAIN}}:5432/${{PGDATABASE}}
'),
            conn_max_age=600,
        )
    }
except:
    # Fallback to sqlite if no database URL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# STATIC FILES
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CLOUDINARY - With fallback
try:
    import cloudinary
    cloudinary.config(
        cloud_name=config('dao1puixd'),
        api_key=config('778438643437337'),
        api_secret=config('5wSjVEVRsxPQ-8GUyeekRhnOwOs'),
        secure=True
    )
except:
    print("Cloudinary not configured")

print("✅ Production settings loaded!")
