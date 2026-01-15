"""
WSGI config for chatbot_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')

application = get_wsgi_application()

# Run migrations automatically on startup (HACK for Render free plan)
if os.getenv('RENDER'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput', verbosity=0)
    except Exception as e:
        print("Migration Error:", e)
