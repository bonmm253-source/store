import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import Category

def reset_categories():
    # 1. New Category List (Fashion & Tech)
    new_categories = [
        ('Bags', 'Premium leather bags, backpacks, and accessories.'),
        ('Shoes', 'Explore our latest collection of sneakers and official shoes.'),
        ('Home Appliances', 'Premium refrigerators, washing machines, and more.'),
        ('Computer Accessories', 'High-speed mouse, keyboards, and hardware.'),
        ('Phones', 'Latest smartphones and mobile accessories.'),
        ('Others', 'Find unique items and miscellaneous accessories.'),
    ]

    # 2. Delete old/temporary categories (Gold, Silver, Nike, etc.)
    # We filter for categories that are NOT in our new list
    new_names = [name for name, _ in new_categories]
    old_cats = Category.objects.exclude(name__in=new_names)

    deleted_count = old_cats.count()
    old_cats.delete()
    print(f"Deleted {deleted_count} old categories.")

    # 3. Create or Update new categories
    for name, desc in new_categories:
        cat, created = Category.objects.update_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"Created category: {name}")
        else:
            print(f"Updated category: {name}")

    print("\n--- Categories Reset Successfully! ---")

if __name__ == "__main__":
    reset_categories()
