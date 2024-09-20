#!/bin/sh

set -e

# Check if SESSION_KEY is already defined
if [ -z "$SESSION_KEY" ]; then
    SESSION_KEY=$(openssl rand -hex 32)
    export SESSION_KEY
    echo "SESSION_KEY=$SESSION_KEY" >> /etc/environment
    echo "A new SESSION_KEY has been generated."
else
    echo "Using the SESSION_KEY provided by the user."
fi

# Set default PostgreSQL values if not provided
: ${PG_HOST:=postgresql}
: ${PG_PORT:=5432}
: ${PG_USER:=streamfusion}
: ${PG_PASS:=streamfusion}
: ${PG_BASE:=streamfusion}

export DATABASE_URL="postgresql://${PG_USER}:${PG_PASS}@${PG_HOST}:${PG_PORT}/${PG_BASE}"

# Wait for the database to be ready
echo "Waiting for database to be ready..."
until PGPASSWORD=$PG_PASS psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_BASE -c '\q'; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
done
echo "Database is ready."

# Function to check if tables exist
check_tables_exist() {
    table_count=$(PGPASSWORD=$PG_PASS psql -h $PG_HOST -p $PG_PORT -U $PG_USER -d $PG_BASE -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    [ "$table_count" -gt 0 ]
}

# Function to check if there are pending migrations
check_pending_migrations() {
    alembic current > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        return 0
    else
        return 1
    fi
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    alembic upgrade head
    if [ $? -ne 0 ]; then
        echo "Error: Database migrations failed."
        exit 1
    fi
    echo "Database migrations completed successfully."
}

# Check if tables exist, if not, run migrations
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

echo "Starting the application..."
python -m stream_fusion