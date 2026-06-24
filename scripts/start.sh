#!/usr/bin/env sh
set -eu

echo "Starting Audio Extract App"
echo "Running database migrations"

attempt=1
max_attempts=5

until python manage.py migrate --noinput; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "Database migrations failed after $attempt attempts"
    exit 1
  fi

  echo "Database not ready yet; retrying migration in 5 seconds ($attempt/$max_attempts)"
  attempt=$((attempt + 1))
  sleep 5
done

echo "Ensuring initial admin user"
python manage.py create_admin_from_env

echo "Starting web server on port ${PORT:-8000}"
exec gunicorn audio_extract_app.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
