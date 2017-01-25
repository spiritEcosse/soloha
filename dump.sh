#!/usr/bin/env bash

FILE=$(date +"%Y-%m-%d-%H.%M.%S").all.json
FILE_ARCHIVE=$FILE.bz2
PROJECT_LOCATION=/home/h5782c/zapchastie
FIXTURES=$PROJECT_LOCATION/data/fixtures

function dumpdata() {
    source /home/h5782c/virtualenv/zapchastie/2.7/bin/activate
    $PROJECT_LOCATION/manage.py dumpdata --indent 4 --natural-primary --natural-foreign -e contenttypes -e auth.Permission -e sessions -e admin > $FIXTURES/$FILE
    bzip2 -f $FIXTURES/$FILE
    $PROJECT_LOCATION/dropbox_uploader.sh upload $FIXTURES/$FILE_ARCHIVE /
    rm -f $FIXTURES/*.all.json*
}

dumpdata 2>&1 | tee $PROJECT_LOCATION/error.log
