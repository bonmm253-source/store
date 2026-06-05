import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import Category

def init_categories():
    categories = [
        ('Home Appliances', 'Premium refrigerators, washing machines, and more.'),
        ('Computer Accessories', 'High-speed mouse, keyboards, and hardware.'),
        ('Phones', 'Latest smartphones and mobile accessories.'),
    ]

    for name, desc in categories:
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
        if created:
            print(f"Created category: {name}")
        else:
            print(f"Category already exists: {name}")

if __name__ == "__main__":
    init_categories()
