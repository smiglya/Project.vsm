# Source Generated with Decompyle++
# File: test.cpython-312.pyc (Python 3.12)

'''
Упрощенные настройки для тестирования API без внешних зависимостей.
'''
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-insecure-test-key-for-development-only'
DEBUG = True
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '*']
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
    'drf_spectacular']
LOCAL_APPS = [
    'apps.mileage_calculator']
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
        'NAME': 'test_vsm_db',
        'USER': 'vsm_user',
        'PASSWORD': 'vsm_password',
        'HOST': 'db',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_vsm_db',
        }
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake' } }
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
STATICFILES_DIRS = [
    BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny'],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json' }
SPECTACULAR_SETTINGS = {
    'TITLE': 'VSM Калькулятор Пробега API',
    'DESCRIPTION': 'API для расчета пробега и планирования ТО электропоездов',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False }
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
EXTERNAL_API_URL = os.environ.get('EXTERNAL_API_URL', 'https://api.example.com')
EXTERNAL_API_KEY = os.environ.get('EXTERNAL_API_KEY', 'test-key')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler' } },
    'root': {
        'handlers': [
            'console'],
        'level': 'INFO' },
    'loggers': {
        'django': {
            'handlers': [
                'console'],
            'level': 'INFO',
            'propagate': False },
        'apps.mileage_calculator': {
            'handlers': [
                'console'],
            'level': 'DEBUG',
            'propagate': False } } }
