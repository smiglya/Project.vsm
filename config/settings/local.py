# Source Generated with Decompyle++
# File: local.cpython-312.pyc (Python 3.12)

'''
Настройки для локальной разработки.
'''
from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    '*'
]

# Настройки базы данных для Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'vsm_db'),
        'USER': os.environ.get('DB_USER', 'vsm_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'vsm_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis настройки
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}

if 'LOGGING' in locals():
    LOGGING['loggers']['django']['level'] = 'DEBUG'
    LOGGING['loggers']['apps']['level'] = 'DEBUG'

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost'
    ]

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CORS_ALLOW_ALL_ORIGINS = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery настройки для тестирования
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
