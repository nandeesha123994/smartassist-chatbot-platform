import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_platform.settings')

application = get_wsgi_application()

# Auto-migrate on Render if using SQLite
db_engine = os.getenv("DB_ENGINE", "")
if "sqlite3" in db_engine:
    try:
        from django.core.management import call_command
        call_command("migrate", interactive=False)
        print("SQLite auto-migration completed")
    except Exception as e:
        print("Migration error:", e)
