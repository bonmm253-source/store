import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import Category

categories = Category.objects.all()
for c in categories:
    print(f"Category: {c.name}")
    print(f"Description: {c.description}")
    print("-" * 20)
