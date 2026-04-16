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

try:
    user = User.objects.get(username='admin')
except User.DoesNotExist:
    print("Admin user 'admin' does not exist. Run create_admin.py first.")
    sys.exit(1)

user.set_password(admin_password)
user.save()
print("Admin password reset successfully.")
