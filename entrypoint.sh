python manage.py collectstatic --noinput

gunicorn -w 3 -t 3 -b 0.0.0.0:8080 canadahackers.wsgi:application
