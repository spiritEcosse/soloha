#!/usr/bin/env bash

./manage.py collectstatic --noinput
./manage.py makemigrations
./manage.py migrate
./manage.py rebuild_index --noinput
./manage.py build_solr_schema > solr.xml
./manage.py rebuild_index --noinput
gunicorn composeexample.wsgi -w 2 -b 0.0.0.0:8000 --reload
