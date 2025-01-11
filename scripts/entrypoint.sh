#!/bin/bash

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset
source /opt/pysetup/.venv/bin/activate

#
#
#postgres_ready() {
#/opt/pysetup/.venv/bin/python << END
#import sys
#
#import psycopg
#
#try:
#    psycopg.connect(
#        dbname="${POSTGRES_DB}",
#        user="${POSTGRES_USER}",
#        password="${POSTGRES_PASSWORD}",
#        host="${POSTGRES_HOST}",
#        port="${POSTGRES_PORT}",
#    )
#except psycopg.OperationalError:
#    sys.exit(-1)
#sys.exit(0)
#
#END
#}
#until postgres_ready; do
#  >&2 echo 'Waiting for PostgreSQL to become available...'
#  sleep 1
#done
#>&2 echo 'PostgreSQL is available'

export DJANGO_ENV=production

exec "$@"
