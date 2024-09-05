#!/bin/sh

# Load environment variables from .env file
DEBUG=$(python -c "from decouple import config; print(config('DEBUG'))")

    python3 manage.py migrate && \
    python3 manage.py create_superuser && \
    python3 manage.py seeder && \
    python3 manage.py tailwind install  --no-input && \
    python3 manage.py tailwind build  --no-input && \
    python3 manage.py collectstatic --noinput

if [ "$DEBUG" = "True" ]; then
    echo "Running in development mode"
    python3 manage.py runserver 0.0.0.0:8000
else
    echo "Running in production mode"
    gunicorn --bind 0.0.0.0:8000 urjwan.wsgi:application
fi
