#!/bin/bash
python manage.py migrate                  # Apply database migrations
python manage.py collectstatic --noinput  # Collect static files

# Prepare log files and start outputting logs to stdout
touch /srv/logs/uwsgi.log
touch /srv/logs/access.log
touch /srv/log/logfile
tail -n 0 -f /srv/logs/*.log &

# Start UWSGI processes
echo Starting uwsgi.
uwsgi --ini /srv/catalogue_service/docker_config_files/uwsgi.ini
#python manage.py runserver 