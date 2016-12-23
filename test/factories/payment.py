import factory

from soloha.core.loading import get_model

__all__ = [
    'SourceTypeFactory', 'SourceFactory', 'TransactionFactory',
]


class SourceTypeFactory(factory.DjangoModelFactory):
    name = 'Creditcard'
    code = 'creditcard'

    class Meta:
        model = get_model('payment', 'SourceType')


class SourceFactory(factory.DjangoModelFactory):
    order = factory.SubFactory(
        'test.factories.OrderFactory')
    source_type = factory.SubFactory(SourceTypeFactory)

    class Meta:
        model = get_model('payment', 'Source')


class TransactionFactory(factory.DjangoModelFactory):
    amount = factory.LazyAttribute(lambda obj: obj.source.order.total_incl_tax)
    reference = factory.LazyAttribute(lambda obj: obj.source.order.number)
    source = factory.SubFactory(SourceFactory)
    status = 'authorised'

    class Meta:
        model = get_model('payment', 'Transaction')

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        date_created = kwargs.pop('date_created', None)
        instance = super(TransactionFactory, cls)._create(
            target_class, *args, **kwargs)

        if date_created:
            instance.date_created = date_created
            instance.save()
        return instance
