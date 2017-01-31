############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

FROM python:3.5

# Set the file maintainer (your name - the file's author)
MAINTAINER Igor Shevchenko

# Set env variables used in this Dockerfile (add a unique prefix, such as DOCKYARD)
# Local directory with project source
#ENV DOCKYARD_SRC=/home/igor/web/soloha
# Directory in container for all project files
#ENV DOCKYARD_SRVHOME=/srv
# Directory in container for project source files
#ENV DOCKYARD_SRVPROJ=/srv/soloha

#ENV PYTHONUNBUFFERED 1

# Update the default application repository sources list
#RUN apt-get update && apt-get -y upgrade
#RUN apt-get install -y python python-pip

# Create application subdirectories
#WORKDIR $DOCKYARD_SRVHOME
#RUN mkdir media static logs
RUN mkdir /code
#VOLUME ["$DOCKYARD_SRVHOME/media/", "$DOCKYARD_SRVHOME/logs/"]

# Copy entrypoint script into the image
#WORKDIR $DOCKYARD_SRVPROJ
WORKDIR /code
#COPY ./docker-entrypoint.sh /
#ENTRYPOINT ["/docker-entrypoint.sh"]

# Copy application source code to SRCDIR
#COPY $DOCKYARD_SRC $DOCKYARD_SRVPROJ

# Install Python dependencies
ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/


# Port to expose
#EXPOSE 80230
