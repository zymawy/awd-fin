#!/bin/sh

# Load environment variables from .env file
DEBUG=$(python -c "from decouple import config; print(config('DEBUG'))")

RUN SECRET_KEY=nothing python manage.py tailwind install --no-input;
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input;
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input;

    python3 manage.py migrate && \
    python3 manage.py create_superuser && \
    python3 manage.py seeder

if [ "$DEBUG" = "True" ]; then
    echo "Running in development mode"
    python3 manage.py runserver 0.0.0.0:8000
else
    echo "Running in production mode"
    gunicorn --bind 0.0.0.0:8000 urjwan.wsgi:application
fi
