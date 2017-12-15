#!/bin/bash

# Prepare log files and start outputting logs to stdout
touch /srv/log/logfile
#tail -n 0 -f /srv/logs/*.log &

#sudo service celeryd start
export C_FORCE_ROOT=true
#tail -n 0 -f /srv/logs/*.log
celery -A catalogue_service beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler