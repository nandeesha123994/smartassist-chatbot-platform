import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')

# Auto-run migrations for SQLite
try:
    from django.core.management import call_command
    db_engine = os.getenv("DB_ENGINE", "")
    if "sqlite3" in db_engine:
        print("Running SQLite migrations...")
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
        print("Migrations completed!")
except Exception as e:
    print("Migration error:", e)

application = get_wsgi_application()
