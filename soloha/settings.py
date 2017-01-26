#  -*- coding: utf-8 -*-
"""
Django settings for soloha project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from oscar import get_core_apps
from oscar.defaults import *
from oscar import OSCAR_MAIN_TEMPLATE_DIR
from django.utils.translation import ugettext_lazy as _
from oscar import get_core_apps
import sys
from soloha import settings_local

BASE_DIR = settings_local.BASE_DIR
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7k!04u9xrvn)n80r6+h-3b!y%vdm6k4f6+*@56u+*7jqw_feul'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = settings_local.DEBUG
THUMBNAIL_DEBUG = settings_local.THUMBNAIL_DEBUG
ALLOWED_HOSTS = settings_local.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = \
    [
        'flat',
        'dal',
        'dal_select2',
        'django.contrib.admin',
        'django.contrib.sitemaps',
        'debug_toolbar',
        # 'django_select2',
        # 'bootstrap_pagination',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
        'django.contrib.redirects',
        'compressor',
        'widget_tweaks',
        'djangular',
        'mptt',
        'feincms',
        'easy_thumbnails',
        'filer',
        'apps.contacts',
        'apps.ex_sites',
        'apps.ex_redirects',
        'import_export',
        'ckeditor',
        'apps.sitemap',
        'apps.subscribe',
        'apps.ex_flatpages',
        'bootstrap_pagination',
        'memoize',
        'debug_panel',
    ] + get_core_apps(
        [
            'apps.catalogue', 'apps.promotions', 'apps.partner', 'apps.search', 'apps.order',
            'apps.basket', 'apps.checkout', 'apps.customer', 'apps.dashboard.promotions', 'apps.offer',
            'apps.voucher', 'apps.analytics',
        ]
    )

SITE_ID = 1

MIDDLEWARE_CLASSES = settings_local.MIDDLEWARE_CLASSES
ROOT_URLCONF = 'soloha.urls'

DJANGO_LIVE_TEST_SERVER_ADDRESS = "localhost:8000-8010,8080,9200-9300"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR
        ],
        'OPTIONS': {
            'loaders': [
                # ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'django.template.loaders.eggs.Loader',
                # ]),
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'soloha.core.context_processors.context_data',
                'apps.ex_flatpages.context_processors.context_data',
            ],
        },
    },
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


WSGI_APPLICATION = 'soloha.wsgi.application'

RECOMMENDED_PRODUCTS = 20
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': settings_local.DB_BACKEND,
        'NAME': settings_local.DB_NAME,
        'USER': settings_local.DB_USER,
        'PASSWORD': settings_local.DB_PASSWORD,
        'HOST': settings_local.DB_HOST,
        'POST': settings_local.DB_PORT,
        'ATOMIC_REQUESTS': settings_local.DB_ATOMIC_REQUESTS,
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('ru', _('Russia')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

import os
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', x)
from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATE_DIRS = (
    location('templates'),
)

STATIC_URL = settings_local.STATIC_URL
STATIC_ROOT = settings_local.FOLDER_STATIC_ROOT
MEDIA_ROOT = os.path.join(BASE_DIR,  'media')
MEDIA_URL = "/media/"

STATICFILES_DIRS = settings_local.STATICFILES_DIRS

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

CKEDITOR_JQUERY_URL = os.path.join(STATIC_URL, 'bower_components/jquery/dist/jquery.min.js')
CKEDITOR_UPLOAD_PATH = 'images/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': 'auto',
    },
}

CACHES = settings_local.CACHES
CACHE_MIDDLEWARE_SECONDS = settings_local.CACHE_MIDDLEWARE_SECONDS
KEY_PREFIX = settings_local.KEY_PREFIX

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

IMAGE_NOT_FOUND = 'image_not_found.jpg'
ADMINS = (('igor', 'shevchenkcoigor@gmail.com'),)
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS
OSCAR_FROM_EMAIL = DEFAULT_FROM_EMAIL

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
#         # 'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         # 'URL': 'http://127.0.0.1:8983/solr',
#         # 'INCLUDE_SPELLING': True,
#     },
# }

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://127.0.0.1:9200/',
#         'INDEX_NAME': 'haystack',
#         'EXCLUDED_INDEXES': [
#             'myproject.search.search_indexes.CoreProductIndex',
#              'oscar.apps.search.search_indexes.ProductIndex',
#              ]
#     },
# }


HAYSTACK_CONNECTIONS = settings_local.HAYSTACK_CONNECTIONS


# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
#         'URL': 'http://127.0.0.1:8983/solr/',
#     },
# }

# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

OSCAR_MISSING_IMAGE_URL = 'image_not_found.jpg'

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Cancelled': (),
}
OSCAR_DEFAULT_CURRENCY = u'UAH'
OSCAR_CURRENCY_FORMAT = u'#,##0.## грн.'
OSCAR_PRODUCTS_PER_PAGE = 24

THUMBNAIL_HIGH_RESOLUTION = True
FILER_CANONICAL_URL = 'sharing/'
FILER_DEBUG = DEBUG
FILER_ENABLE_LOGGING = DEBUG
FILER_DUMP_PAYLOAD = False

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    #'easy_thumbnails.processors.scale_and_crop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters',
)

THUMBNAIL_DUMMY = True
THUMBNAIL_FORCE_OVERWRITE = True
# OSCAR_PRODUCT_SEARCH_HANDLER = ""
#
# USE_LESS = True
#
# COMPRESS_PRECOMPILERS = (
#     ('text/less', 'lessc {infile} {outfile}'),
# )
#
# COMPRESS_OFFLINE_CONTEXT = {
#     # this is the only default value from compressor itself
#     'STATIC_URL': STATIC_URL,
#     'use_less': USE_LESS,
# }

MAX_COUNT_PRODUCT = 20
MAX_COUNT_CATEGORIES = 7

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/',
        'TIMEOUT': 60 * 10,
        'INDEX_NAME': 'test_index',
    },
}

IMPORT_EXPORT_USE_TRANSACTIONS = True

THUMBNAIL_ALIASES = {
    '': {
        'category_icon': {'size': (50, 30), 'crop': True},
        'phone_icon': {'size': (50, 30), 'crop': True},
        'subcategory_image': {'size': (94, 62), 'crop': True},
        'category_banner': {'size': (574, 230), 'crop': True},
        'basket_quick': {'size': (85, 50), 'crop': True},
        'basket_quick_product_image': {'size': (30, 30), 'crop': True},
        'basket_content': {'size': (150, 150), 'crop': True},
        'checkout': {'size': (150, 150), 'crop': True},
        'home_thumb_slide': {'size': (1170, 392), 'crop': True},
    },
}

OSCAR_SHOP_NAME = 'soloha'
DEBUG_TOOLBAR_CONFIG = settings_local.DEBUG_TOOLBAR_CONFIG
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
USE_ETAGS = not DEBUG

HTML_MINIFY = not DEBUG
KEEP_COMMENTS_ON_MINIFYING = False
EXCLUDE_FROM_MINIFYING = ('^spirit/', )
SECURE_CONTENT_TYPE_NOSNIFF = True
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
