import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')

application = get_wsgi_application()

# -------------------------------------------------
# AUTO MIGRATE SQLITE ON RENDER STARTUP (REQUIRED)
# -------------------------------------------------
if os.getenv("DB_ENGINE") == "django.db.backends.sqlite3":
    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
        print("SQLite auto-migration completed.")
    except Exception as e:
        print("SQLite auto-migration error:", e)
