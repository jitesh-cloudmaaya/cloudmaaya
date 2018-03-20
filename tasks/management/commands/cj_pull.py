from django.core.management.base import BaseCommand
from tasks.product_feed import ProductFeed

class Command(BaseCommand):
    help = 'Used to pull CJ data feeds'
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

        # rest of task is todo
    except Exception as e:
        self.stdout.write(self.style.ERROR("Failed"))
        self.stdout.write(self.style.ERROR(e))
