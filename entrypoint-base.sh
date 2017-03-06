#!/usr/bin/env bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-9001}
GOSU_USER=spirit

echo "Starting with UID : $USER_ID"
useradd --shell /bin/bash -u $USER_ID -o -c "" -m $GOSU_USER
export HOME=/home/$GOSU_USER

exec /usr/local/bin/gosu $GOSU_USER "$@"
