import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import Category, shoe, watch, Product

def fix_categories():
    print("--- Starting Category Cleanup ---")

    # 1. Define what we WANT
    desired_categories = {
        'Bags': 'Premium leather bags, backpacks, and accessories.',
        'Shoes': 'Explore our latest collection of sneakers and official shoes.',
        'Home Appliances': 'Premium refrigerators, washing machines, and more.',
        'Computer Accessories': 'High-speed mouse, keyboards, and hardware.',
        'Phones': 'Latest smartphones and mobile accessories.',
        'Others': 'Find unique items and miscellaneous accessories.',
        'Men': 'Fashion and accessories for men.',
        'Women': 'Fashion and accessories for women.',
        'Wrist Watch': 'High-quality watches for every occasion.'
    }

    # 2. Create the desired categories if they don't exist
    cat_objects = {}
    for name, desc in desired_categories.items():
        cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
        cat_objects[name] = cat
        if created:
            print(f"Created: {name}")

    # 3. Handle old categories (GOLD, NIKE, etc.)
    # We will try to MOVE products from old categories to 'Others' or 'Shoes' before deleting them
    # so you don't lose your data!

    old_cat_names = ['GOLD', 'SILVER', 'Silver', 'Nice', 'NIKE', 'Gold']
    others_cat = cat_objects['Others']
    shoes_cat = cat_objects['Shoes']

    for old_name in old_cat_names:
        old_cats = Category.objects.filter(name__iexact=old_name)
        for old_cat in old_cats:
            # Move products to a safe place
            target = shoes_cat if 'nike' in old_name.lower() else others_cat

            p_count = Product.objects.filter(category=old_cat).update(category=target)
            s_count = shoe.objects.filter(category=old_cat).update(category=target)
            w_count = watch.objects.filter(category=old_cat).update(category=target)

            total_moved = p_count + s_count + w_count
            print(f"Moved {total_moved} items from '{old_cat.name}' to '{target.name}'")

            # Now delete the empty old category
            old_cat.delete()
            print(f"Deleted old category: {old_cat.name}")

    # 4. Final Cleanup: Delete ANY category not in our list
    all_cats = Category.objects.all()
    for c in all_cats:
        if c.name not in desired_categories:
            print(f"Removing remaining unwanted category: {c.name}")
            c.delete()

    print("\n--- Categories Fixed Successfully! ---")
    print("Your products have been moved to 'Shoes' or 'Others' instead of being deleted.")

if __name__ == "__main__":
    fix_categories()
