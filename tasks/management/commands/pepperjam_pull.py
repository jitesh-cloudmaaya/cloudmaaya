from django.core.management.base import BaseCommand
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to Pull PepperJam Data Feeds - Warning Very Slow (1-2 Hours)!'

    def handle(self, *args, **options):
        try:
            pf = ProductFeed('catalogue_service/pepperjam.yaml')

            self.stdout.write(self.style.WARNING("Creating temp directory for cleaned files"))
            pf.make_temp_dir()

            self.stdout.write(self.style.WARNING("Pulling and cleaning product data"))
            pf.clean_data()

            self.stdout.write(self.style.WARNING("Update API products table"))
            pf.load_cleaned_data()

            self.stdout.write(self.style.SUCCESS("Successfully updated API products table"))
            self.stdout.write(self.style.SUCCESS("Now setting deleted for non-upserted products"))
            pf.set_deleted_network_products()
            self.stdout.write(self.style.SUCCESS("Successfully set non-upserted products to deleted"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))
