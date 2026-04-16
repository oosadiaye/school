import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.development')
django.setup()

from django.conf import settings
if not settings.DEBUG:
    print("ERROR: This script must only run with DEBUG=True settings (development). Aborting.")
    sys.exit(1)

from django.contrib.auth import get_user_model
User = get_user_model()

admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser('admin', 'admin@example.com', admin_password)
    print(f"Admin user created successfully!")
else:
    print("Admin user already exists")
