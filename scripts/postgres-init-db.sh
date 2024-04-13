#!/usr/bin/env bash

set -eu

echo '=== SETUP DATABASE'

echo '--- setting up users'

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" << EOF
CREATE USER hacker WITH PASSWORD '$HACKER_PASSWORD';
ALTER ROLE hacker SET client_encoding TO 'utf8';
ALTER ROLE hacker SET default_transaction_isolation TO 'read committed';
ALTER ROLE hacker SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hackers TO hacker;
\c hackers
GRANT ALL ON SCHEMA public TO hacker;
EOF
