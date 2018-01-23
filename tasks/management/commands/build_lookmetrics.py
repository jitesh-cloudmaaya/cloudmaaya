from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Used to build the LookMetrics table, shopping_tool_lookmetrics'

    def handle(self, *args, **options):
        try:
            cursor = connection.cursor()
            self.stdout.write(self.style.WARNING("Looking for look_metrics.sql file in project"))
            etl_file = open('tasks/look_metrics_sql/look_metrics.sql')
            self.stdout.write(self.style.WARNING("Getting SQL commands from file"))
            statement = etl_file.read()
            statements = statement.split(';')
            self.stdout.write(self.style.WARNING("Attempting to run SQL commands and build LookMetrics table"))
            try:
                with transaction.atomic():
                    for i in range(0, len(statements) - 1):
                        cursor.execute(statements[i])
            finally:
                cursor.close()
                self.stdout.write(self.style.WARNING("Successfully built shopping_tool_lookmetrics table"))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Failed"))
            self.stdout.write(self.style.ERROR(e))
