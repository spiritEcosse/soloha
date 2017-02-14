import os, sys

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

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://solr:8983/solr/collection1',
        'EXCLUDED_INDEXES': ['apps.catalogue.search_indexes.ProductIndex'],
    },
}

FOLDER_STATIC = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static_root/'
FOLDER_STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip("/"))

STATICFILES_DIRS = (
    FOLDER_STATIC,
)

DEBUG_TOOLBAR_CONFIG = {
    'RENDER_PANELS': DEBUG,
    'JQUERY_URL': os.path.join(STATIC_URL, 'bower_components/jquery/dist/jquery.min.js'),
}

CACHE_MIDDLEWARE_SECONDS = 24 * 60 * 60
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_DIR
KEY_PREFIX = CACHE_MIDDLEWARE_KEY_PREFIX

MIDDLEWARE_CLASSES = (
    'django.middleware.cache.UpdateCacheMiddleware',
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
    'apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
    }
}
