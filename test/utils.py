from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.backends.db import SessionStore
from django.core.signing import Signer
from django.test import RequestFactory as BaseRequestFactory

from apps.basket.models import Basket
from apps.partner.strategy import Selector


class RequestFactory(BaseRequestFactory):
    selector = Selector()

    def request(self, user=None, basket=None, **request):
        request = super(RequestFactory, self).request(**request)
        request.user = user or AnonymousUser()
        request.session = SessionStore()
        request._messages = FallbackStorage(request)

        # Mimic basket middleware
        request.strategy = self.selector.strategy(request=request, user=request.user)
        request.basket = basket or Basket()
        request.basket.strategy = request.strategy
        request.basket_hash = Signer().sign(basket.pk) if basket else None
        request.cookies_to_delete = []

        return request