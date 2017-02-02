############################################################
# Dockerfile to run a Django-based web application
# Based on an Ubuntu Image
############################################################

# Set the base image to use to Ubuntu
FROM ubuntu:14.04

FROM python:3.5

# Set the file maintainer (your name - the file's author)
MAINTAINER Igor Shevchenko

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code
RUN pip install -r requirements.txt
COPY . /code

COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
