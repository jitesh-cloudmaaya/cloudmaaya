from django.core.management.base import BaseCommand
from shopping_tool.models import LookProduct
from catalogue_service.settings_local import AWS_ACCESS_KEY, AWS_SECRET_KEY, COLLAGE_BUCKET_NAME, COLLAGE_BUCKET_KEY
import boto3
from django.db import connection



class Command(BaseCommand):
    help = 'Used to convert existing  - Warning Very Slow (Hours)!'

    def handle(self, *args, **options):

        client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        #image_bucket = client.lookup(COLLAGE_BUCKET_NAME)



        keys = []

        kwargs = {'Bucket': COLLAGE_BUCKET_NAME}
        while True:
            resp = client.list_objects_v2(**kwargs)
            for obj in resp['Contents']:
                if COLLAGE_BUCKET_KEY in obj['Key']:
                    keys.append(obj['Key'])

            try:
                kwargs['ContinuationToken'] = resp['NextContinuationToken']
            except KeyError:
                break

        for key in keys:
            print key
            response = client.copy_object(Bucket=COLLAGE_BUCKET_NAME,
                                  Key=key,
                                  ContentType="image/png",
                                  MetadataDirective="REPLACE",
                                  CopySource=COLLAGE_BUCKET_NAME + "/" + key)
            client.put_object_acl(Bucket=COLLAGE_BUCKET_NAME, Key=key, ACL='public-read')