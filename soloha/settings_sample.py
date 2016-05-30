__author__ = 'igor'

DEFAULT_FROM_EMAIL = ''
EMAIL_COMPANY = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEBUG = True
THUMBNAIL_DEBUG = DEBUG
AUTORELOAD = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        }
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = 'soloha_'

MIDDLEWARE_CLASSES = (
    # """START for production"""
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
    # """END for production"""
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ALLOWED_HOSTS = ['localhost']

DB_BACKEND = 'django.db.backends.postgresql_psycopg2'
DB_NAME = 'soloha'
DB_USER = 'soloha'
DB_PASSWORD = 'pass'
DB_HOST = ''
DB_PORT = ''
DB_ATOMIC_REQUESTS = True

DB_BACKEND_MYSQL = 'django.db.backends.mysql',
DB_NAME_MYSQL = 'soloha',
DB_USER_MYSQL = 'soloha',
DB_PASSWORD_MYSQL = ''


MY_SERVER = {'server': '78.24.216.187', 'path': '/home/igor/web/www/cinema/', 'venv': '.env/bin/activate'}
