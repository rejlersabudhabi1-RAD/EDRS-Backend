release: python manage.py migrate --noinput
web: gunicorn rejlers_api.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-file - --access-logfile - --error-logfile - --log-level info