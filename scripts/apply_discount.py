import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import shoe

def apply_discount(target):
    shoes = shoe.objects.filter(target_audience=target)
    for s in shoes:
        s.discount_price = float(s.price) * 0.9
        s.save()
    print(f"Applied 10% discount to {shoes.count()} items in {target}")

if __name__ == "__main__":
    apply_discount('Male')
    apply_discount('Female')
