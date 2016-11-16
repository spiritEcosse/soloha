import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.basename(BASE_DIR)

DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_USER = 'shevchenkcoigor@gmail.com'
EMAIL_HOST_PASSWORD = 'fuaskzfiocehxzyj'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEBUG = True
THUMBNAIL_DEBUG = DEBUG

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

FOLDER_STATIC = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static_root/'
FOLDER_STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))

STATICFILES_DIRS = (
    FOLDER_STATIC,
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': PROJECT_DIR,
    }
}

DEBUG_TOOLBAR_CONFIG = {
    'RENDER_PANELS': DEBUG,
    'JQUERY_URL': os.path.join(STATIC_URL, 'bower_components/jquery/dist/jquery.min.js'),
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIR
KEY_PREFIX = CACHE_MIDDLEWARE_KEY_PREFIX

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware',
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
    # 'django.middleware.cache.FetchFromCacheMiddleware',
)

ALLOWED_HOSTS = ['*']

DB_BACKEND = 'django.db.backends.postgresql_psycopg2'
DB_NAME, DB_USER, DB_PASSWORD = (PROJECT_DIR, ) * 3
DB_HOST = 'localhost'
DB_PORT = ''
DB_ATOMIC_REQUESTS = True
