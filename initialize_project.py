import os
import django
import secrets
import string

# 1. Update .env with a real Secret Key if it's the default
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()

    if 'django-insecure-your-secret-key-here' in content:
        alphabet = string.ascii_letters + string.digits + string.punctuation.replace('"', '').replace("'", '').replace('$', '')
        new_key = ''.join(secrets.choice(alphabet) for i in range(50))
        content = content.replace('django-insecure-your-secret-key-here', new_key)
        with open(env_path, 'w') as f:
            f.write(content)
        print("✅ SECRET_KEY updated in .env")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drop.settings')
django.setup()

from django.core.management import call_command
from web.models import User, Category

# 2. Run Migrations
print("⏳ Running migrations...")
call_command('migrate')
print("✅ Migrations complete")

# 3. Create Superuser
admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'adminpassword123'

if not User.objects.filter(username=admin_username).exists():
    print(f"⏳ Creating superuser '{admin_username}'...")
    User.objects.create_superuser(admin_username, admin_email, admin_password)
    print(f"✅ Superuser created. (Login: {admin_username} / {admin_password})")
else:
    print(f"ℹ️ Superuser '{admin_username}' already exists.")

# 6. Populate Categories
categories = ['Shoes', 'Watches', 'Male', 'Female', 'Collections']
print("⏳ Populating categories...")
for cat_name in categories:
    obj, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f"   - Created category: {cat_name}")
print("✅ Categories ready")

print("\n🚀 Initialization complete! You can now run 'docker-compose up'")
