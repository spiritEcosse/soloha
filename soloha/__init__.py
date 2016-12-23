import os

# Use 'dev', 'beta', or 'final' as the 4th element to indicate release type.
VERSION = (1, 0, 0, 'dev')


def get_short_version():
    return '%s.%s' % (VERSION[0], VERSION[1])


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    # Append 3rd digit if > 0
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    elif VERSION[3] != 'final':
        version = '%s %s' % (version, VERSION[3])
        if len(VERSION) == 5:
            version = '%s %s' % (version, VERSION[4])
    return version


MAIN_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

CORE_INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'debug_toolbar',
    # 'django_select2',
    # 'bootstrap_pagination',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'apps.analytics',
    'apps.checkout',
    'apps.address',
    'apps.shipping',
    'apps.catalogue',
    'apps.catalogue.reviews',
    'apps.partner',
    'apps.basket',
    'apps.payment',
    'apps.offer',
    'apps.order',
    'apps.customer',
    'apps.promotions',
    'apps.search',
    'apps.voucher',
    'apps.wishlists',
    'apps.contacts',
    'apps.ex_sites',
    'apps.ex_redirects',
    'apps.sitemap',
    'apps.subscribe',
    'apps.ex_flatpages',
    'compressor',
    'widget_tweaks',
    'djng',
    'mptt',
    'easy_thumbnails',
    'filer',
    'import_export',
    'ckeditor',
    'bootstrap_pagination',
    'debug_panel',
    'haystack',
    'django_tables2',
    'django_extensions',
    'django_jenkins',
]


def get_core_apps(overrides=None):
    """
    Return a list of oscar's apps amended with any passed overrides
    """
    if not overrides:
        return CORE_INSTALLED_APPS

    # Conservative import to ensure that this file can be loaded
    # without the presence Django.
    from django.utils import six
    if isinstance(overrides, six.string_types):
        raise ValueError(
            "get_core_apps expects a list or tuple of apps "
            "to override")

    def get_app_label(app_label, overrides):
        pattern = app_label.replace('apps.', '')
        for override in overrides:
            if override.endswith(pattern):
                if 'dashboard' in override and 'dashboard' not in pattern:
                    continue
                return override
        return app_label

    apps = []
    for app_label in CORE_INSTALLED_APPS:
        apps.append(get_app_label(app_label, overrides))
    return apps

