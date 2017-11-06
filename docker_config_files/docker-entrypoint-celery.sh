#!/bin/bash

# Prepare log files and start outputting logs to stdout
touch /srv/log/logfile
#tail -n 0 -f /srv/logs/*.log &

#sudo service celeryd start
export C_FORCE_ROOT=true
#tail -n 0 -f /srv/logs/*.log
celery worker -A catalogue_service.celeryconf -Q default -n default_1