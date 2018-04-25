from django.core.management.base import BaseCommand
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to pull CJ data feeds'

    def handle(self, *args, **options):
        try:
            pf = ProductFeed('catalogue_service/cj.yaml')

            self.stdout.write(self.style.WARNING("Pulling full files from FTP"))
            pf.get_files_sftp()

            self.stdout.write(self.style.WARNING("Decompressing files"))
            pf.decompress_data()

            self.stdout.write(self.style.WARNING("Cleaning files"))
            pf.clean_data()

            self.stdout.write(self.style.WARNING("Update API products table"))
            pf.load_cleaned_data()

            self.stdout.write(self.style.SUCCESS("Sucessfully updated API products table"))
            self.stdout.write(self.style.SUCCESS("Now setting deleted for non-upserted products"))
            pf.set_deleted_network_products()
            self.stdout.write(self.style.SUCCESS("Successfully set non-upserted products to deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))
