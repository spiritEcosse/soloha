from soloha.settings import *

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DATABASE_NAME', ':memory:'),
    },
}

INSTALLED_APPS = [
    # contains models we need for testing
    'tests._site.model_tests_app',
    'tests._site.myauth',

    # Use a custom partner app to test overriding models.  I can't
    # find a way of doing this on a per-test basis, so I'm using a
    # global change.
] + soloha.get_core_apps(['tests._site.apps.partner', 'tests._site.apps.customer'])

AUTH_USER_MODEL = 'myauth.User'

TEMPLATES[0]['DIRS'].append(soloha.MAIN_TEMPLATE_DIR)

HAYSTACK_CONNECTIONS = {'default': {'ENGINE': 'haystack.backends.simple_backend.SimpleEngine'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
ROOT_URLCONF = 'tests._site.urls'
LOGIN_REDIRECT_URL = '/accounts/'
DEBUG = False
DDF_DEFAULT_DATA_FIXTURE = 'tests.dynamic_fixtures.DynamicDataFixtureClass'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
THUMBNAIL_DEBUG = DEBUG

INITIAL_ORDER_STATUS = 'A'
ORDER_STATUS_PIPELINE = {'A': ('B',), 'B': ()}
INITIAL_LINE_STATUS = 'a'
LINE_STATUS_PIPELINE = {'a': ('b', ), 'b': ()}

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
