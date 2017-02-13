#!/usr/bin/env bash

./manage.py collectstatic --noinput
./manage.py makemigrations
./manage.py migrate
./manage.py build_solr_schema > $(SOLR_SCHEMA)/schema.xml
./manage.py rebuild_index --noinput
gunicorn composeexample.wsgi -w 2 -b 0.0.0.0:8000 --reload
