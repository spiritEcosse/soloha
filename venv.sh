#!/usr/bin/env bash

source `which virtualenvwrapper.sh`
rmvirtualenv $1
mkvirtualenv $1 --python=`which python3`

# Python 3 (replace ~/.virtualenvs on variable - where locate ~/.virtualenvs or something like)
# mkvirtualenv $1 -p /usr/bin/python3.4 ~/.virtualenvs/$1

# Install libs in virtual environment
pip install -r requirements.txt

# Update migrations
./manage.py makemigrations analytics checkout address shipping catalogue reviews partner basket payment offer order customer promotions search voucher wishlists contacts ex_sites ex_redirects sitemap subscribe ex_flatpages

# Apply migrate
./manage.py migrate

# Collectstatic
./manage.py collectstatic --noinput

# Create cache table
./manage.py createcachetable

# Unzip
tar -xzvf data/fixtures/all.tar.gz -C data/fixtures/

# Load initial data from fixtures.
./manage.py loaddata data/fixtures/*.json
./manage.py oscar_populate_countries
./manage.py clear_index --noinput
./manage.py update_index catalogue

