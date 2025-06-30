#!/bin/bash
set -e

# Load env dari .env tanpa \r error
source <(tr -d '\r' < /env_vars/.env)

echo "[db-init] Waiting for PostgreSQL on host: $POSTGRES_HOST..."
until pg_isready -h $POSTGRES_HOST -U "$POSTGRES_USER"; do
  sleep 2
done

echo "[db-init] Creating user if not exists..."
PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$POSTGRES_DB" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '$AIRFLOW_USER') THEN
      CREATE ROLE $AIRFLOW_USER LOGIN PASSWORD '$AIRFLOW_PASS';
    END IF;
  END
  \$\$;
EOSQL

echo "[db-init] Creating database if not exists..."
PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$POSTGRES_DB" <<-EOSQL
  SELECT 'CREATE DATABASE $AIRFLOW_DB OWNER $AIRFLOW_USER'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$AIRFLOW_DB')\gexec
EOSQL

echo "[db-init] Waiting for $AIRFLOW_DB database to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$AIRFLOW_DB" -c '\q' 2>/dev/null; do
  sleep 5
done

echo "[db-init] Granting full privileges on schema public..."
# Ke airflow DB
PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$AIRFLOW_DB" <<-EOSQL
  ALTER SCHEMA public OWNER TO $AIRFLOW_USER;
  GRANT USAGE, CREATE ON SCHEMA public TO $AIRFLOW_USER;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $AIRFLOW_USER;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $AIRFLOW_USER;
EOSQL

# Ke healthcare DB
PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -h "$POSTGRES_HOST" -d "$POSTGRES_DB" <<-EOSQL
  ALTER SCHEMA public OWNER TO $AIRFLOW_USER;
  GRANT USAGE, CREATE ON SCHEMA public TO $AIRFLOW_USER;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $AIRFLOW_USER;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $AIRFLOW_USER;
EOSQL