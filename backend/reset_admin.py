import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()
print(f"Password reset for admin user!")
