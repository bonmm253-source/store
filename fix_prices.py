import os
import django
import random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import shoe, watch

updated_shoes = 0
for s in shoe.objects.all():
    if not s.price or s.price == 0:
        s.price = random.randint(20, 150)
        s.save()
        updated_shoes += 1

updated_watches = 0
for w in watch.objects.all():
    if not w.price or w.price == 0:
        w.price = random.randint(50, 300)
        w.save()
        updated_watches += 1

print(f"Done! Updated {updated_shoes} shoes and {updated_watches} watches with missing prices.")
