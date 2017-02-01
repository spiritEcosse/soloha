############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

FROM python:3.5

# Set the file maintainer (your name - the file's author)
MAINTAINER Igor Shevchenko
ENV PROJECT=soloha

# Directory in container for project source files
ENV DOCKYARD_SRVPROJ=/srv/$PROJECT

RUN mkdir -p $DOCKYARD_SRVPROJ
WORKDIR $DOCKYARD_SRVPROJ
ADD . $DOCKYARD_SRVPROJ
RUN pip install -r requirements.txt

RUN ./manage.py collectstatic --noinput
RUN ./manage.py makemigrations
RUN ./manage.py migrate
