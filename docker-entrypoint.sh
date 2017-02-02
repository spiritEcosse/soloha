#!/usr/bin/env bash

python manage.py collectstatic --noinput

python manage.py makemigrations
python manage.py migrate catalogue
python manage.py migrate

# Prepare log files and start outputting logs to stdout
#touch /srv/logs/gunicorn.log
#touch /srv/logs/access.log
#tail -n 0 -f /srv/logs/*.log &

# Start Gunicorn processes
#echo Starting Gunicorn.
#exec /usr/local/bin/gunicorn soloha.wsgi:application \
#    --name soloha \
#    --bind 0.0.0.0:8000 \
#    --workers 3 \
#    --log-level=info \
#    --log-file=/srv/logs/gunicorn.log \
#    --access-logfile=/srv/logs/access.log \
#    "$@"
