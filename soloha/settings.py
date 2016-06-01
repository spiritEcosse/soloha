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
from soloha import settings_local
from django.utils.translation import ugettext_lazy as _
from oscar import get_core_apps
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(BASE_DIR)

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
        'suit',
        'django.contrib.admin',
        'django.contrib.sitemaps',
        'debug_toolbar',
         # 'django_select2',
         # 'bootstrap_pagination',
         # 'djangular',
         # 'ckeditor',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.sites',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.flatpages',
        'compressor',
        'widget_tweaks',
        'djangular',
        'mptt',
        'feincms',
        'easy_thumbnails',
        # 'smart_load_tag',
    ] + get_core_apps(['apps.catalogue', 'apps.promotions', 'apps.partner'])

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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
                'soloha.core.context_processors.context_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'soloha.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

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
            'ENGINE': settings_local.DB_BACKEND,
            'NAME': settings_local.DB_NAME,
            'USER': settings_local.DB_USER,
            'PASSWORD': settings_local.DB_PASSWORD,
            'HOST': settings_local.DB_HOST,
            'POST': settings_local.DB_PORT,
            'ATOMIC_REQUESTS': settings_local.DB_ATOMIC_REQUESTS,
        },
        # 'mysql': {
        #     'ENGINE': settings_local.DB_BACKEND_MYSQL,
        #     'NAME': settings_local.DB_NAME_MYSQL,
        #     'USER': settings_local.DB_USER_MYSQL,
        #     'PASSWORD': settings_local.DB_PASSWORD_MYSQL,
        #     'HOST': settings_local.DB_HOST_MYSQL,
        #     'POST': settings_local.DB_PORT_MYSQL,
        #     'ATOMIC_REQUESTS': settings_local.DB_ATOMIC_REQUESTS_MYSQL,
        # },
        # 'default': {
        #     'ENGINE': 'django.db.backends.sqlite3',
        #     'NAME': location('db.sqlite3'),
        #     'USER': '',
        #     'PASSWORD': '',
        #     'HOST': '',
        #     'PORT': '',
        #     'ATOMIC_REQUESTS': True
        # },
    }

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('en', _('England')),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

import os
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', x)
from oscar import OSCAR_MAIN_TEMPLATE_DIR
TEMPLATE_DIRS = (
    location('templates'),
    OSCAR_MAIN_TEMPLATE_DIR,
)

STATIC_URL = '/static_root/'
STATIC_ROOT = os.path.join(BASE_DIR,  'static_root')
MEDIA_ROOT = os.path.join(BASE_DIR,  'media')
MEDIA_URL = "/media/"

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js'
CKEDITOR_UPLOAD_PATH = 'images/'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 650,
    },
}

CACHES = settings_local.CACHES
CACHE_MIDDLEWARE_SECONDS = settings_local.CACHE_MIDDLEWARE_SECONDS
CACHE_MIDDLEWARE_KEY_PREFIX = settings_local.CACHE_MIDDLEWARE_KEY_PREFIX

IMAGE_NOT_FOUND = 'image_not_found.jpg'
ADMINS = (('igor', 'shevchenkcoigor@gmail.com'),)
DEFAULT_FROM_EMAIL = settings_local.DEFAULT_FROM_EMAIL
EMAIL_COMPANY = settings_local.EMAIL_COMPANY
EMAIL_HOST_USER = settings_local.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = settings_local.EMAIL_HOST_PASSWORD
EMAIL_HOST = settings_local.EMAIL_HOST
EMAIL_PORT = settings_local.EMAIL_PORT
EMAIL_USE_TLS = settings_local.EMAIL_USE_TLS

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/',
    },
}

OSCAR_MISSING_IMAGE_URL = 'image_not_found.jpg'

OSCAR_INITIAL_ORDER_STATUS = 'Pending'
OSCAR_INITIAL_LINE_STATUS = 'Pending'
OSCAR_ORDER_STATUS_PIPELINE = {
    'Pending': ('Being processed', 'Cancelled',),
    'Being processed': ('Processed', 'Cancelled',),
    'Cancelled': (),
}

THUMBNAIL_DUMMY = True
THUMBNAIL_FORCE_OVERWRITE = True
OSCAR_DEFAULT_CURRENCY = 'UAH'
OSCAR_PRODUCTS_PER_PAGE = 24
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

