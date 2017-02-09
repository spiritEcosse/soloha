#!/usr/bin/env bash

source `which virtualenvwrapper.sh`
rmvirtualenv $1
mkvirtualenv $1

# Install libs in virtual environment
pip install -r requirements.txt

# Update migrations
git clean -xf **/migrations/** # temporary solution, use because rmvirtualenv is use
./manage.py makemigrations

# Apply migrate
# I know that a bad approach, it is temporary, if I have time to change no more than the right one.
./manage.py migrate
./manage.py migrate catalogue
./manage.py migrate

# Collectstatic
./manage.py collectstatic --noinput

# Create cache table
./manage.py createcachetable

# Load initial data from fixtures.
./manage.py loaddata data/fixtures/all.json.bz2
./manage.py oscar_populate_countries
./manage.py rebuild_index --noinput
#sudo touch /var/solr/data/$1/conf/schema.xml
#./manage.py build_solr_schema >> /var/solr/data/$1/conf/schema.xml
#sudo chown solr:solr /var/solr/data/$1/conf/schema.xml
