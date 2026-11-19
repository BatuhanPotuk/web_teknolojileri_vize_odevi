import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-yemekhane-auth-gizli-anahtar-2026')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# Veritabanı (Primary & Replica)
DB_ADI = os.environ.get('DB_ADI', 'yemekhane')
DB_KULLANICI = os.environ.get('DB_KULLANICI', 'yemekhane_app')
DB_SIFRE = os.environ.get('DB_SIFRE', 'Uyg_2026')
DB_PORT = os.environ.get('DB_PORT', '3306')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_ADI,
        'USER': DB_KULLANICI,
        'PASSWORD': DB_SIFRE,
        'HOST': os.environ.get('DB_YAZMA_HOST', 'mysql-primary'),
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
    'replica': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_ADI,
        'USER': DB_KULLANICI,
        'PASSWORD': DB_SIFRE,
        'HOST': os.environ.get('DB_OKUMA_HOST', 'mysql-replica'),
        'PORT': DB_PORT,
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

# Redis Ayarları
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', '6379'))

# Dahili Güvenlik Anahtarı
INTERNAL_TOKEN = os.environ.get('INTERNAL_TOKEN', 'yemekhane_ic_gizli_anahtar_2026')

# Saat Dilimi Kuralları
LANGUAGE_CODE = 'tr-tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
