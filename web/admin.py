from django.contrib import admin

# Register your models here.
from .models import User, shoe, Category, Order, watch

admin.site.register(User)
admin.site.register(shoe)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(watch)