import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from web.models import shoe, watch, Category

print("Updating shoes and watches with discount_price to show Flash Sales...")
# Just grab the first few and set discount_price
shoes = shoe.objects.all()
for index, s in enumerate(shoes):
    s.target_audience = 'Male' if index % 2 == 0 else 'Female'
    # Make some of them flash sales
    if index < 2:
        s.discount_price = float(s.price) * 0.8
    s.save()

watches = watch.objects.all()
for index, w in enumerate(watches):
    if index < 2:
        w.discount_price = float(w.price) * 0.8
    w.save()

print("Shoes count:", shoes.count())
print("Watches count:", watches.count())
print("Done")
