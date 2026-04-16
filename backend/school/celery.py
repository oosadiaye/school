"""Celery app configuration for TIMS."""
import os
from celery import Celery

# Default settings module for 'celery' CLI command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.development')

app = Celery('school')

# Load settings from Django with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in each installed app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Print task request — useful for debugging worker setup."""
    print(f'Request: {self.request!r}')
