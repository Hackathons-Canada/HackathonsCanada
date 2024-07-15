#!/usr/bin/env bash

set -eu

echo '=== SETUP DATABASE'

echo '--- setting up users'

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" << EOF
CREATE USER hacker WITH PASSWORD 'change_me_pleaseeeeeeeeee';
ALTER ROLE hacker SET client_encoding TO 'utf8';
ALTER ROLE hacker SET default_transaction_isolation TO 'read committed';
ALTER ROLE hacker SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hackathons TO hacker;
\c hackathons
GRANT ALL ON SCHEMA public TO hacker;
EOF

cat ./pg_dump.sql.gz | gzip -d | psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" # update pg_dump.sql.gz
