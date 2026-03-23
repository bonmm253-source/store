import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import shoe

shoes = shoe.objects.all()
for i, s in enumerate(shoes):
    s.target_audience = 'Male' if i % 2 == 0 else 'Female'
    # Any custom logic for recent additions
    if 'Heel' in s.name or 'women' in s.name.lower():
        s.target_audience = 'Female'
    elif 'Sneaker' in s.name:
        s.target_audience = 'Male'
    s.save()

print("All shoes updated to Male or Female.")
