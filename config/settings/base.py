# Source Generated with Decompyle++
# File: base.cpython-312.pyc (Python 3.12)

'''
Базовые настройки Django для проекта VSM.
'''
from celery.schedules import crontab
import os
from pathlib import Path
from decouple import config
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY', default = 'django-insecure-2#p_*t2r&giog@7q3!a!6!0=5^lz$o8+nsz0db*$kjdg5&1sj(')
DEBUG = config('DEBUG', default = True, cast = bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles']
THIRD_PARTY_APPS = [
    'rest_framework',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results']
LOCAL_APPS = [
    'apps.mileage_calculator']
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'] } }]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default = 'vsm_db'),
        'USER': config('DB_USER', default = 'vsm_user'),
        'PASSWORD': config('DB_PASSWORD', default = 'vsm_password'),
        'HOST': config('DB_HOST', default = 'localhost'),
        'PORT': config('DB_PORT', default = '5432'),
        'OPTIONS': {
            'connect_timeout': 10 } } }
REDIS_URL = config('REDIS_URL', default = 'redis://localhost:6379/1')
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient' } } }
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default = 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default = 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = [
    'json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    'daily-mileage-sync': {
        'task': 'apps.mileage_calculator.tasks.daily_mileage_sync',
        'schedule': crontab(hour = 2, minute = 0) },
    'generate-maintenance-alerts': {
        'task': 'apps.mileage_calculator.tasks.generate_maintenance_alerts',
        'schedule': crontab(hour = 8, minute = 0) },
    'cleanup-old-cache': {
        'task': 'apps.mileage_calculator.tasks.cleanup_old_cache',
        'schedule': crontab(hour = 1, minute = 0) } }
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' }]
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = []
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema' }
SPECTACULAR_SETTINGS = {
    'TITLE': 'VSM Калькулятор пробега API',
    'DESCRIPTION': 'API для системы отслеживания пробега и планирования ТО электропоездов',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True }
MAX_UPLOAD_SIZE = config('MAX_UPLOAD_SIZE', default = 5242880, cast = int)
ALLOWED_EXTENSIONS = config('ALLOWED_EXTENSIONS', default='xlsx,xls', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{' },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{' } },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'vsm.log',
            'formatter': 'verbose' },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple' } },
    'root': {
        'handlers': [
            'console',
            'file'],
        'level': 'INFO' },
    'loggers': {
        'django': {
            'handlers': [
                'console',
                'file'],
            'level': config('LOG_LEVEL', default = 'INFO'),
            'propagate': False },
        'apps': {
            'handlers': [
                'console',
                'file'],
            'level': 'DEBUG',
            'propagate': False } } }
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8080',
    'http://127.0.0.1:8080']
CORS_ALLOW_CREDENTIALS = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
EXTERNAL_API_URL = config('EXTERNAL_API_URL', default = 'https://api.example.com')
EXTERNAL_API_KEY = config('EXTERNAL_API_KEY', default = 'your-api-key-here')
