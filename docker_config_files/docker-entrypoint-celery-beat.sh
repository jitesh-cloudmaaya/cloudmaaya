#!/bin/bash

# Prepare log files and start outputting logs to stdout
touch /srv/log/logfile
#tail -n 0 -f /srv/logs/*.log &

#sudo service celeryd start
export C_FORCE_ROOT=true
#tail -n 0 -f /srv/logs/*.log

NEW_RELIC_CONFIG_FILE=newrelic.ini
export NEW_RELIC_CONFIG_FILE

newrelic-admin run-program celery -A catalogue_service beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler