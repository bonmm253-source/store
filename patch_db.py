import os
import django

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drop.settings")
django.setup()

from web.models import Category
from django.db import connection

# Direct sqlite query to wipe out old rows with invalid foreign keys before Django migration complains
with connection.cursor() as cursor:
    try:
        cursor.execute("INSERT OR IGNORE INTO web_category (id, name) VALUES (1, 'Default')")
        cursor.execute("UPDATE web_shoe SET category_id = 1 WHERE category_id NOT IN (SELECT id FROM web_category)")
        cursor.execute("UPDATE web_watch SET category_id = 1 WHERE category_id NOT IN (SELECT id FROM web_category)")
    except Exception as e:
        print(f"Direct update failed first time, maybe column is named 'category': {e}")
        try:
            cursor.execute("UPDATE web_shoe SET category = 1 WHERE category NOT IN (SELECT id FROM web_category)")
            cursor.execute("UPDATE web_watch SET category = 1 WHERE category NOT IN (SELECT id FROM web_category)")
        except Exception as e2:
            print(f"Direct update failed second time: {e2}")

print("Patched DB using Django cursor.")
