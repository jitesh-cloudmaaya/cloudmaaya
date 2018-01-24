from django.core.management.base import BaseCommand, CommandError
from tasks.product_feed_py.pepperjam import get_data, get_merchants

class Command(BaseCommand):
    help = 'Used to Pull PepperJam Merchants List and Update the Application DB'

    def handle(self, *args, **options):
        get_merchants()