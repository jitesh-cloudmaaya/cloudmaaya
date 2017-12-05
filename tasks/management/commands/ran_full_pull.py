from django.core.management.base import BaseCommand, CommandError
from catalogue_service.settings_local import DATABASES
from tasks.product_feed import ProductFeed


class Command(BaseCommand):
    help = 'Used to Pull Ran Data Feeds - Full Pull - Warning Very Low (Hours)!'

    def handle(self, *args, **options):
        try:
            
            pf = ProductFeed("catalogue_service/ran_yaml")

            self.stdout.write(self.style.WARNING("Pulling Files from FTP"))
            pf.get_files_ftp()

            self.stdout.write(self.style.WARNING("Loading Data to DB and Updating Products"))
            pf.process_data()
        except Exception as ex:
            self.stdout.write(self.style.ERROR(ex))