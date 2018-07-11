from django.core.management.base import BaseCommand
from django.db import connection, transaction, connections
import os
from catalogue_service.settings import BASE_DIR

class Command(BaseCommand):
    help = 'Used to update the AllumeClient360 table, allume_client_360'

    def handle(self, *args, **options):
        try:
            # self.stdout.write(self.style.WARNING("Updating Client 360 table"))
            # add_client_to_360_raw(self, 'tasks/client_360_sql/update_client_360.sql',
            #                       'WHERE wu.id IN (SELECT u0.ID FROM wp_users u0 WHERE u0.last_modified > (SELECT MAX(a0.last_updated) FROM allume_client_360 a0));')
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))



def add_client_to_360_raw(self, task_sql, user_filter):
    cursor = connection.cursor()
    etl_read_file = open(os.path.join(BASE_DIR, 'tasks/client_360_sql/client_360_read.sql'))
    etl_file = open(os.path.join(BASE_DIR, task_sql))
    read_statement = etl_read_file.read()
    read_statement = read_statement.replace('$USER_FILTER', user_filter)
    print "updating User to Client 360"
    quiz_orders_data = []
    try:
        read_statements = read_statement.split(';')
        for i in range(0, len(read_statements)):
            read_statement = read_statements[i]
            if read_statement.strip():  # avoid 'query was empty' operational error
                with connections['allume_read_only'].cursor() as read_cursor:
                    read_cursor.execute(read_statement)
                    quiz_orders_data = read_cursor.fetchall()
        statement = etl_file.read()
        statements = statement.split(';')
        with transaction.atomic():
            for i in range(0, len(statements)):
                statement = statements[i]
                if statement.strip():  # avoid 'query was empty' operational error
                    if 'insert into' in statement.lower():
                        cursor.executemany(statement, quiz_orders_data)
                    else:
                        cursor.execute(statement)
    finally:
        cursor.close()
        self.stdout.write(self.style.SUCCESS("Successfuly updated Client 360 table"))