import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')

# AUTO-MIGRATE ON STARTUP (Fix for missing tables on Render)
try:
    from django.core.management import call_command
    print("WSGI: Attempting to run migrations...")
    call_command('migrate')
    print("WSGI: Migrations completed successfully.")
except Exception as e:
    print(f"WSGI: Migration failed: {e}")

application = get_wsgi_application()

# Run migrations AFTER application loads
def run_sqlite_migrations():
    from django.conf import settings
    from django.core.management import call_command

    db_engine = settings.DATABASES["default"]["ENGINE"]

    if "sqlite3" in db_engine:
        try:
            print("[INFO] Running SQLite migrations after app init...")
            call_command("migrate", interactive=False)
            print("[SUCCESS] SQLite migrations done!")
        except Exception as e:
            print("[ERROR] Migration failed:", e)

run_sqlite_migrations()
