from oscar.apps.customer import config


class CustomerConfig(config.CustomerConfig):
    name = 'apps.customer'

    def ready(self):
        from . import receivers  # noqa
        from .alerts import receivers  # noqa
