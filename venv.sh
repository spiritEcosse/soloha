#!/usr/bin/env bash

source `which virtualenvwrapper.sh`
rmvirtualenv $1
mkvirtualenv $1

# Install libs in virtual environment
pip install -r requirements.txt

# Update migrations
./manage.py makemigrations

# Apply migrate
./manage.py migrate

# Collectstatic
./manage.py collectstatic --noinput

# Create cache table
./manage.py createcachetable

# Load initial data from fixtures.
./manage.py loaddata all.json.bz2
./manage.py oscar_populate_countries
./manage.py rebuild_index --noinput
#sudo touch /var/solr/data/$1/conf/schema.xml
#./manage.py build_solr_schema >> /var/solr/data/$1/conf/schema.xml
#sudo chown solr:solr /var/solr/data/$1/conf/schema.xml
