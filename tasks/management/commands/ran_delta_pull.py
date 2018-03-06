from django.core.management.base import BaseCommand
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to Pull Ran Data Feeds - Incremental Pull'

    def handle(self, *args, **options):
        try:
            pf = ProductFeed('catalogue_service/ran_delta.yaml')

            self.stdout.write(self.style.WARNING("Pulling delta files from FTP"))
            #pf.get_files_ftp()

            self.stdout.write(self.style.WARNING("Decompressing files"))
            #pf.decompress_data()

            self.stdout.write(self.style.WARNING("Cleaning files"))
            #pf.clean_data()

            self.stdout.write(self.style.WARNING("Update API products table"))
            pf.load_cleaned_data()

            self.stdout.write(self.style.SUCCESS("Successfully updated API products table"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))