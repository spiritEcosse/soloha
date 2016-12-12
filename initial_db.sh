#!/usr/bin/env bash

source `which virtualenvwrapper.sh`
workon $1

# Update migrations
./manage.py makemigrations

# Apply migrate
./manage.py migrate

# Load initial data from fixtures.
./manage.py loaddata data/fixtures/*.json
./manage.py oscar_populate_countries --initial-only
