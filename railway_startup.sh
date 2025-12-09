#!/bin/bash
# Railway startup script with proper error handling

echo "🚀 Starting Railway deployment..."

# Check for required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  WARNING: DATABASE_URL not set!"
    echo "Setting fallback database configuration..."
    export DATABASE_URL="postgresql://postgres:password@localhost:5432/railway"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  WARNING: SECRET_KEY not set!"
    echo "Setting fallback secret key (NOT FOR PRODUCTION!)..."
    export SECRET_KEY="railway-fallback-secret-key-change-in-production"
fi

if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo "Setting DJANGO_SETTINGS_MODULE..."
    export DJANGO_SETTINGS_MODULE="rejlers_api.settings"
fi

# Set PORT if not set
if [ -z "$PORT" ]; then
    export PORT=8000
    echo "PORT not set, using default: 8000"
fi

echo "📦 Environment variables configured"
echo "🔧 PORT: $PORT"
echo "🗄️  DATABASE_URL: ${DATABASE_URL:0:30}..."

# Run migrations (with timeout and error handling)
echo "🔄 Running database migrations..."
timeout 30s python manage.py migrate --noinput 2>&1 || {
    echo "⚠️  Migration failed or timed out (non-fatal, continuing...)"
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear 2>&1 || {
    echo "⚠️  Static files collection failed (non-fatal, continuing...)"
}

# Start Gunicorn
echo "🌐 Starting Gunicorn server on port $PORT..."
exec gunicorn rejlers_api.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --preload
