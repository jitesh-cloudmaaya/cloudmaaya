from django.core.management.base import BaseCommand
from shopping_tool.models import Look
from catalogue_service.settings_local import AWS_ACCESS_KEY, AWS_SECRET_KEY, COLLAGE_BUCKET_NAME, COLLAGE_BUCKET_KEY
import boto3
from django.db import connection



class Command(BaseCommand):
    help = 'Used to Pull Ran Data Feeds - Full Pull - Warning Very Slow (Hours)!'

    def handle(self, *args, **options):
        looks_count = Look.objects.filter(is_legacy=False).count()

        print looks_count
        # limit_start = 0
        # limit_increment = 100
        # processed = ''
        # skipped = ''
        # while limit_start <= looks_count + limit_increment:
        #     with connection.cursor() as cursor:
        #         cursor.execute("""
        #             SELECT id, collage
        #             from allume_looks
        #             where is_legacy = 0
        #             limit %s, %s
        #         """, [limit_start, limit_increment])
        #         looks = cursor.fetchall()
        #     for look in looks:
        #         collage_image_name = "%s/collage_%s.png" % (COLLAGE_BUCKET_KEY, look[0])

        #         if (look[1] != None) and (len(look[1]) > 1000):
        #             collage_image_data = look[1][look[1].find(",")+1:]
        #             collage_image_data = collage_image_data.decode('base64')

        #             client = boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        #             client.put_object(Body=collage_image_data, Bucket=COLLAGE_BUCKET_NAME, Key=collage_image_name)
        #             client.put_object_acl(Bucket=COLLAGE_BUCKET_NAME, Key=collage_image_name, ACL='public-read')

        #             processed = processed + str(look[0]) + ','
        #         else:
        #             skipped = skipped + str(look[0]) + ','
        #     limit_start = limit_start + limit_increment
        # print 'end: ' + str(skipped)
        # print 'end: ' + str(processed)