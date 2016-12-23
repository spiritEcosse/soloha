from django.test import TestCase

from apps.customer.models import ProductAlert
from soloha.core.compat import get_user_model
from test.factories import create_product
from test.factories import UserFactory


User = get_user_model()


class TestAnAlertForARegisteredUser(TestCase):

    def setUp(self):
        user = UserFactory()
        product = create_product()
        self.alert = ProductAlert.objects.create(user=user,
                                                 product=product)

    def test_defaults_to_active(self):
        self.assertTrue(self.alert.is_active)
