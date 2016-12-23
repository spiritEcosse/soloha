import factory

from apps.partner.strategy import Selector
from apps.basket.models import Basket, LineAttribute


class BasketFactory(factory.DjangoModelFactory):

    @factory.post_generation
    def set_strategy(self, create, extracted, **kwargs):
        # Load default strategy (without a user/request)
        self.strategy = Selector().strategy()

    class Meta:
        model = Basket


class BasketLineAttributeFactory(factory.DjangoModelFactory):
    option = factory.SubFactory('test.factories.OptionFactory')

    class Meta:
        model = LineAttribute
