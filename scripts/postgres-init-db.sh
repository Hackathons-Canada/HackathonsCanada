#!/usr/bin/env bash

set -eu

echo '=== SETUP DATABASE'

# --- Create the database only if it doesn't exist
echo '--- creating database (if not exists)'

psql -v ON_ERROR_STOP=1 --username "postgres" <<-EOSQL
SELECT 'CREATE DATABASE $POSTGRES_DB'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_DB')\gexec
EOSQL

echo '--- setting up users'

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOF
CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
ALTER ROLE $POSTGRES_USER SET client_encoding TO 'utf8';
ALTER ROLE $POSTGRES_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $POSTGRES_USER SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
\c $POSTGRES_DB
GRANT ALL ON SCHEMA public TO $POSTGRES_USER';
EOF
