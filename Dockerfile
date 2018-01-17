############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:16.04.3

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
RUN apt-get --ignore-missing update && apt-get -y upgrade
RUN apt-get install -y python python-pip
RUN apt-get install -y libpq-dev python-dev
RUN apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN apt-get install -y socat
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y python-cffi
RUN apt-get install -y libffi6 libffi-dev
RUN apt-get install -y python-setuptools
RUN apt-get install -y python3-setuptools
RUN apt-get install -y nano
RUN apt-get install -y wkhtmltopdf

###################################
##### Install Headless Chrome #####
## https://gist.github.com/ziadoz/3e8ab7e944d02fe872c3454d17af31a5

# Versions
#ENV CHROME_DRIVER_VERSION='curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE'
#ENV SELENIUM_STANDALONE_VERSION="3.4.0"
#ENV SELENIUM_SUBDIR="3.4"

# Remove existing downloads and binaries so we can start from scratch.
#RUN apt-get remove google-chrome-stable
##RUN rm ~/chromedriver_linux64.zip
##RUN sudo rm /usr/local/bin/chromedriver

# Install dependencies.
#RUN apt-get update
#RUN apt-get install -y unzip openjdk-8-jre-headless xvfb libxi6 libgconf-2-4
#RUN apt-get install -y curl

# Install Chrome.
#RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
#RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
#RUN apt-get -y update
#RUN apt-get -y install google-chrome-stable

# Install ChromeDriver
#RUN wget -N http://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip -P ~/
#RUN unzip ~/chromedriver_linux64.zip -d ~/
#RUN rm ~/chromedriver_linux64.zip
#RUN mv -f ~/chromedriver /usr/local/bin/chromedriver
#RUN chown root:root /usr/local/bin/chromedriver
#RUN chmod 0755 /usr/local/bin/chromedriver

# Install Selenium.
#RUN wget -N http://selenium-release.storage.googleapis.com/$SELENIUM_SUBDIR/selenium-server-standalone-$SELENIUM_STANDALONE_VERSION.jar -P ~/
#RUN mv -f ~/selenium-server-standalone-$SELENIUM_STANDALONE_VERSION.jar /usr/local/bin/selenium-server-standalone.jar
#RUN chown root:root /usr/local/bin/selenium-server-standalone.jar
#RUN chmod 0755 /usr/local/bin/selenium-server-standalone.jar


###################################

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
COPY ./docker_config_files/docker-entrypoint-test-circleci.sh /
COPY ./docker_config_files/docker-entrypoint-web-circleci.sh /
ENTRYPOINT ["/docker-entrypoint-web.sh"]
