from django.core.management.base import BaseCommand
from shopping_tool.models import LookProduct
from catalogue_service.settings_local import AWS_ACCESS_KEY, AWS_SECRET_KEY, COLLAGE_BUCKET_NAME, COLLAGE_BUCKET_KEY
import boto3
from django.db import connection



class Command(BaseCommand):
    help = 'Used to convert existing  - Warning Very Slow (Hours)!'

    def handle(self, *args, **options):
        look_products_count = LookProduct.objects.count()
        client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)


        print look_products_count
        limit_start = 0
        limit_increment = 100
        limit_end = limit_increment
        processed = ''
        skipped = ''
        while limit_start <= look_products_count + limit_increment:
            look_products = LookProduct.objects.order_by('id').all()[limit_start:limit_end]
            for lookproduct in look_products:

                if lookproduct.cropped_image_code != None:
                    if len(lookproduct.cropped_image_code) > 1000:
                        cropped_image_name = lookproduct.generate_cropped_image_s3_path()
                        cropped_image_url = "https://%s.s3.amazonaws.com/%s" % (COLLAGE_BUCKET_NAME, cropped_image_name)
                        cropped_image_data = lookproduct.cropped_image_code[lookproduct.cropped_image_code.find(",")+1:]
                        cropped_image_data = cropped_image_data.decode('base64')

                        
                        #Delete Existing Collage
                        try:
                            old_cropped_image_code = lookproduct.cropped_image_code.split("%s/" % (COLLAGE_BUCKET_NAME))[1]
                            print "Deleting %s" % (old_cropped_image_code)
                            client.delete_object(Bucket=COLLAGE_BUCKET_NAME, Key=old_cropped_image_code)
                            
                        except:
                            print "Invalid S3 Key Name"

                        #Save New Collage to S3
                        client.put_object(Body=cropped_image_data, Bucket=COLLAGE_BUCKET_NAME, Key=cropped_image_name, ContentType='image/png')
                        client.put_object_acl(Bucket=COLLAGE_BUCKET_NAME, Key=cropped_image_name, ACL='public-read')
                        print "Saved %s" % (cropped_image_url)
                       

                        lookproduct.cropped_image_code = cropped_image_url
                        lookproduct.save()
                    else:
                        print "Skipped Product, already a URL"
                else:
                    print "Skipped"


            limit_start = limit_start + limit_increment
            limit_end = limit_end + limit_increment