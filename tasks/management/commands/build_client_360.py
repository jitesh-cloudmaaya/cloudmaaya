from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Used to build the AllumeClient360 table, allume_client_360'

    def handle(self, *args, **options):
        try:
            cursor = connection.cursor()
            etl_file = open('tasks/client_360_sql/client_360.sql')
            statement = etl_file.read()
            statements = statement.split(';')
            self.stdout.write(self.style.WARNING("Building Client 360 table"))
            try:
                with transaction.atomic():
                    for i in range(0, len(statements)):
                        statement = statements[i]
                        if statement.strip(): # avoid 'query was empty' operational error
                            cursor.execute(statement)
            finally:
                cursor.close()
                self.stdout.write(self.style.SUCCESS("Successfuly built Client 360 table"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))
