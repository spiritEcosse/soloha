from django.core.management.base import BaseCommand
from apps.catalogue.models import StockRecordAttribute, VersionAttribute


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        :param args:
        :param options:
        :return:
        """

        self.stdout.write('Successfully.')
