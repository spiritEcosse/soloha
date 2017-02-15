#!/usr/bin/env bash

#sleep 10s
sleep 10s
#. .env
. .env
#./manage.py collectstatic --noinput
./manage.py collectstatic --noinput
#./manage.py makemigrations
./manage.py makemigrations
#./manage.py migrate
./manage.py migrate
#./manage.py loaddata $FIXTURES
./manage.py loaddata $FIXTURES
#./manage.py build_solr_schema > $LOCAL_SOLR_SCHEMA
./manage.py build_solr_schema > $LOCAL_SOLR_SCHEMA
#./manage.py rebuild_index --noinput
./manage.py rebuild_index --noinput
#gunicorn soloha.wsgi -w 2 -b 0.0.0.0:8000 --reload
gunicorn soloha.wsgi -w 2 -b 0.0.0.0:8000 --reload
