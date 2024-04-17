import os
from dotenv import load_dotenv  # need for correct work os.environ.get()
from pathlib import Path
"""Next 2 string need for correct work knox Authentication"""
from datetime import timedelta
from rest_framework.settings import api_settings

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()  # need for correct work os.environ.get()
SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = True
RUN_FROM_LOCAL = True

HOST = os.environ.get('HOST_NAME')
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # libraries
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'phonenumber_field',
    'knox',
    'drf_yasg',     # Swagger generator
    'swagger',
    'redis_app',
    'django_celery_beat',
    'django_user_agents',

    # applications
    'company',
    'location',
    'registration',
    'address',
    'image',
    'product',
    'menu',
    'two_factor_authentication',
    'notification_center',
    'celery_app',
]

AUTH_USER_MODEL = 'registration.WebMenuUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
]

ROOT_URLCONF = 'Web_Menu_DA.urls'

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

WSGI_APPLICATION = 'Web_Menu_DA.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# from knox.auth import TokenAuthentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('knox.auth.TokenAuthentication',),    # KNOX settings
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# KNOX settings
REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=24),
    'USER_SERIALIZER': 'registration.serializers.WebMenuUserSerializer',  # displays all data in the view
    'TOKEN_LIMIT_PER_USER': 1,
    'AUTO_REFRESH': True,
    'MIN_REFRESH_INTERVAL': 11 * 60 * 60,
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}

# email settings
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = 2525
EMAIL_USE_SSL = True

# swagger settings
""" 
    For Authorisation in http://127.0.0.1:8000/swagger/:
    1. Login in site and teke Token value
    2. Enter string 'Token + Token value in Authorize button on page 
    http://127.0.0.1:8000/swagger/'
    """
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        },
    },
}

# Caches / Redis settings
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis_app:6379/0',
        'TIMEOUT': 300,  # default timeout for all chash
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'webmenu_redis_cache',
    },
}
CACHE_TIMEOUT = {
    'LocationMenuView': {
        'decorator': 60 * 5,
        'functional': 60 * 2 * 2, },
    '2fa': {
        'Email':  60 * 5, },
}

"""
Redis settings to use Redis db directly. redis_app/redis_app.py
"""
REDIS_HOST = 'redis_app'
REDIS_PORT = 6379
REDIS_DB = 1

# Celery
CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/'
# CELERY_RESULT_BACKEND = is removed in celery 5.x

# to connect to db from local machine
if RUN_FROM_LOCAL:
    DATABASES["default"]["HOST"] = 'localhost'
    DATABASES["default"]["PORT"] = '5433'
    CACHES['default']['LOCATION'] = 'redis://localhost:6379/0'
