#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files
python manage.py create_product_index     # Create the product index if needed

# Prepare log files and start outputting logs to stdout
touch /srv/logs/uwsgi.log
touch /srv/logs/access.log
touch /srv/log/logfile
tail -n 0 -f /srv/logs/*.log &

# Start UWSGI processes
echo Starting uwsgi.
NEW_RELIC_CONFIG_FILE=newrelic.ini
export NEW_RELIC_CONFIG_FILE
newrelic-admin run-program uwsgi --ini /srv/catalogue_service/docker_config_files/uwsgi.ini
