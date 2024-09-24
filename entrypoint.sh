#!/bin/sh

set -e

if [ -z "$SESSION_KEY" ]; then
    SESSION_KEY=$(openssl rand -hex 32)
    export SESSION_KEY
    echo "SESSION_KEY=$SESSION_KEY" >> /etc/environment
    echo "A new SESSION_KEY has been generated."
else
    echo "Using the SESSION_KEY provided by the user."
fi

: ${PG_HOST:=stremio-postgres}
: ${PG_PORT:=5432}
: ${PG_USER:=stremio}
: ${PG_PASS:=stremio}
: ${PG_BASE:=streamfusion}

export DATABASE_URL="postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/${PG_BASE}"

echo "Waiting for PostgreSQL server to be ready..."
until PGPASSWORD=$PG_PASS psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d postgres -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "PostgreSQL server is ready."

if ! PGPASSWORD=$PG_PASS psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d postgres -lqt | cut -d \| -f 1 | grep -qw $PG_BASE; then
    echo "Database $PG_BASE does not exist. Creating..."
    PGPASSWORD=$PG_PASS createdb -h $PG_HOST -p $PG_PORT -U $PG_USER $PG_BASE
    echo "Database $PG_BASE created successfully."
else
    echo "Database $PG_BASE already exists."
fi

check_tables_exist() {
    table_count=$(PGPASSWORD=$PG_PASS psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_BASE -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    [ "$table_count" -gt 0 ]
}

check_pending_migrations() {
    python -m alembic current > /dev/null 2>&1
    [ $? -ne 0 ]
}

run_migrations() {
    echo "Running database migrations..."
    python -m alembic upgrade head
    if [ $? -ne 0 ]; then
        echo "Error: Database migrations failed."
        exit 1
    fi
    echo "Database migrations completed successfully."
}

if ! check_tables_exist; then
    echo "No tables found. Running initial migration..."
    run_migrations
else
    echo "Tables already exist. Checking for pending migrations..."
    if check_pending_migrations; then
        echo "Pending migrations found. Running migrations..."
        run_migrations
    else
        echo "Database schema is up to date."
    fi
fi

echo "---------------------------"
echo "Starting the application..."
echo "---------------------------"
python -m stream_fusion