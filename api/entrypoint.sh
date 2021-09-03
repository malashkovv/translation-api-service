#!/usr/bin/env bash

set -e

if [[ $1 == 'server' ]]; then
  exec gunicorn api.main:app -c /usr/src/app/api/gunicorn_conf.py
fi

exec "$@"
