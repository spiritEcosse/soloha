from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.http import HttpRequest

from test.factories import create_product
from soloha.core.compat import get_user_model
from apps.customer import history
from soloha.core.templatetags.history_tags import get_back_button


User = get_user_model()
COOKIE_NAME = settings.RECENTLY_VIEWED_COOKIE_NAME


class HistoryHelpersTest(TestCase):

    def setUp(self):
        self.product = create_product()

    def test_viewing_product_creates_cookie(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertTrue(COOKIE_NAME in response.cookies)

    def test_id_gets_added_to_cookie(self):
        response = self.client.get(self.product.get_absolute_url())
        request = HttpRequest()
        request.COOKIES[COOKIE_NAME] = response.cookies[COOKIE_NAME].value
        self.assertTrue(self.product.id in history.extract(request))

    def test_get_back_button(self):
        request = HttpRequest()

        request.META['SERVER_NAME'] = 'test'
        request.META['SERVER_PORT'] = 8000
        request.META['HTTP_REFERER'] = 'http://www.google.com'
        backbutton = get_back_button({'request': request})
        self.assertEqual(backbutton, None)

        request.META['HTTP_REFERER'] = 'http://test:8000/search/'
        backbutton = get_back_button({'request': request})
        self.assertTrue(backbutton)
        self.assertEqual(backbutton['title'], 'Back to search results')


class TestAUserWhoLogsOut(TestCase):
    username = 'customer'
    password = 'cheeseshop'
    email = 'customer@example.com'

    def setUp(self):
        self.product = create_product()
        User.objects.create_user(username=self.username,
                                 email=self.email, password=self.password)
        self.client.login(email=self.email, password=self.password)

    def test_has_their_cookies_deleted_on_logout(self):
        response = self.client.get(self.product.get_absolute_url())
        self.assertTrue(COOKIE_NAME in response.cookies)

        response = self.client.get(reverse('customer:logout'))
        self.assertTrue((COOKIE_NAME not in response.cookies)
                        or not self.client.cookies['soloha_recently_viewed_products'].coded_value)