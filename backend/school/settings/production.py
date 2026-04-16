"""Production settings — hardened, SSL enforced, tight CORS."""
from .base import *  # noqa: F401,F403
from decouple import config, Csv

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())
if not ALLOWED_HOSTS:
    raise RuntimeError('ALLOWED_HOSTS must be set in production')

# Tight CORS — only whitelisted frontend origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv())

# SSL / HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Real SMTP email in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int, default=587)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool, default=True)
