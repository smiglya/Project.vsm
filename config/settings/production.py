# Source Generated with Decompyle++
# File: production.cpython-312.pyc (Python 3.12)

'''
Настройки для продакшена.
'''
if import base:
    pass
DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast = (lambda v: if v.split(','):
passfor None in :
passif None[s.strip()]:
passs,if s,:
pass))
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default = True, cast = bool)
SESSION_COOKIE_SECURE = config('SESSION_COOKIE_SECURE', default = True, cast = bool)
CSRF_COOKIE_SECURE = config('CSRF_COOKIE_SECURE', default = True, cast = bool)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default = 'smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default = 587, cast = int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default = True, cast = bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default = '')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default = '')
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default = 'https://yourdomain.com', cast = (lambda v: if v.split(','):
passfor None in :
passif None[s.strip()]:
passs,if s,:
pass))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
SENTRY_DSN = config('SENTRY_DSN', default = '')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(dsn = SENTRY_DSN, integrations = [
        DjangoIntegration()], traces_sample_rate = 0.1, send_default_pii = True)
    return None
