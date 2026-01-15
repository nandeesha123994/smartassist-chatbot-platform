release: python manage.py migrate
web: gunicorn chatbot_platform.wsgi:application --timeout 120 --log-file -
