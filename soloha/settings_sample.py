import sys, os
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

__author__ = 'igor'

DEFAULT_FROM_EMAIL = ''
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
    # 'django.middleware.cache.UpdateCacheMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
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
DB_HOST_MYSQL = ''
DB_PORT_MYSQL = ''
DB_ATOMIC_REQUESTS_MYSQL = True


if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': location('db.sqlite3'),
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
            'ATOMIC_REQUESTS': True
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': DB_BACKEND,
            'NAME': DB_NAME,
            'USER': DB_USER,
            'PASSWORD': DB_PASSWORD,
            'HOST': DB_HOST,
            'POST': DB_PORT,
            'ATOMIC_REQUESTS': DB_ATOMIC_REQUESTS,
        },
        'mysql': {
            'ENGINE': DB_BACKEND_MYSQL,
            'NAME': DB_NAME_MYSQL,
            'USER': DB_USER_MYSQL,
            'PASSWORD': DB_PASSWORD_MYSQL,
            'HOST': DB_HOST_MYSQL,
            'POST': DB_PORT_MYSQL,
            'ATOMIC_REQUESTS': DB_ATOMIC_REQUESTS_MYSQL,
        },
    }
