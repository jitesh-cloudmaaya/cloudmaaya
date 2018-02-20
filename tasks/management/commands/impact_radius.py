from django.core.management.base import BaseCommand
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to pull Impact Radius data feeds'
    try:
        pf = ProductFeed('catalogue_service/impact_radius.yaml')

        self.stdout.write(self.style.WARNING("Pulling full files from FTP"))
        pf.get_files_ftp()

        self.stdout.write(self.style.WARNING("Decompressing files"))
        pf.decompress_data()

        # rest of task is todo
    except Exception as e:
        self.stdout.write(self.style.ERROR("Failed"))
        self.stdout.write(self.style.ERROR(e))