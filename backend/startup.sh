#!/bin/bash
python manage.py migrate analysis_engine 0002 --fake --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
