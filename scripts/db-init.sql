
ALTER ROLE neondb_owner SET client_encoding TO 'utf8';
ALTER ROLE neondb_owner SET default_transaction_isolation TO 'read committed';
ALTER ROLE neondb_owner SET timezone TO 'UTC';

CREATE EXTENSION IF NOT EXISTS postgis;

