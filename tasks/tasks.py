from __future__ import absolute_import, unicode_literals
from celery import task
from django.db import connection, transaction
import os
from catalogue_service.settings import BASE_DIR
from celery_once import QueueOnce

@task(base=QueueOnce)
def build_client_360():
	cursor = connection.cursor()
	etl_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360.sql'))
	statement = etl_file.read()
	cursor.execute(statement)
