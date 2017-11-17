############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:17.04

# Set the file maintainer (your name - the file's author)
MAINTAINER Wes Duenow

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
ENV DOCKYARD_SRC=.
# Directory in container for all project files
ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/catalogue_service

# Update the default application repository sources list
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python python-pip
RUN apt-get install -y libpq-dev python-dev
RUN apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN apt-get install -y socat
RUN apt-get install  -y libmysqlclient-dev
RUN apt-get install -y python-cffi
RUN apt-get install -y libffi6 libffi-dev
RUN apt-get install -y python-setuptools
RUN apt-get install -y python3-setuptools
RUN apt-get install nano
#RUN apt-get install lynx

# Create application subdirectories
WORKDIR $DOCKYARD_SRVHOME
RUN mkdir media static logs log
VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/", "$DOCKYARD_SRVPROJ/static/"]

# Copy application source code to SRCDIR
COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Remove settings_local.py if present
RUN rm -rf /srv/catalogue_service/catalogue_service/settings_local.py

# Install Python dependencies
RUN pip install -r $DOCKYARD_SRVPROJ/requirements.txt  

# Port to expose
EXPOSE 8000

# Copy entrypoint script into the image
WORKDIR $DOCKYARD_SRVPROJ
COPY ./docker_config_files/docker-entrypoint-web.sh /
COPY ./docker_config_files/docker-entrypoint-celery.sh /
COPY ./docker_config_files/docker-entrypoint-celery-beat.sh /
COPY ./docker_config_files/docker-entrypoint-test.sh /
ENTRYPOINT ["/docker-entrypoint-web.sh"]
