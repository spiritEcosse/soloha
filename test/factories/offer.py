import factory

from apps.offer.models import RangeProduct, Benefit, Range, Condition, ConditionalOffer

__all__ = [
    'RangeFactory', 'ConditionFactory', 'BenefitFactory',
    'ConditionalOfferFactory',
]


class RangeFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'Range %d' % n)
    slug = factory.Sequence(lambda n: 'range-%d' % n)

    class Meta:
        model = Range

    @factory.post_generation
    def products(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for product in extracted:
            RangeProduct.objects.create(product=product, range=self)


class BenefitFactory(factory.DjangoModelFactory):
    type = Benefit.PERCENTAGE
    value = 10
    max_affected_items = None
    range = factory.SubFactory(RangeFactory)

    class Meta:
        model = Benefit


class ConditionFactory(factory.DjangoModelFactory):
    type = Condition.COUNT
    value = 10
    range = factory.SubFactory(RangeFactory)

    class Meta:
        model = Condition


class ConditionalOfferFactory(factory.DjangoModelFactory):
    name = 'Test offer'
    benefit = factory.SubFactory(BenefitFactory)
    condition = factory.SubFactory(ConditionFactory)

    class Meta:
        model = ConditionalOffer
