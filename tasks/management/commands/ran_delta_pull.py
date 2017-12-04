from django.core.management.base import BaseCommand, CommandError
from catalogue_service.settings_local import DATABASES
from tasks.product_feed import ProductFeed
import yaml

class Command(BaseCommand):
    help = 'Used to Pull Ran Data Feeds - Incremental Pull'

    def handle(self, *args, **options):
        try:

            pf = ProductFeed("catalogue_service/ran_yaml")

            self.stdout.write(self.style.WARNING("Pulling Files from FTP"))
            pf.get_files_ftp()

            self.stdout.write(self.style.WARNING("Loading Data to DB and Updating Products"))
            pf.process_data()

            self.stdout.write(self.style.WARNING("Updating the API Products Table"))
            pf.update_products_api()
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))