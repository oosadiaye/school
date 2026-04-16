"""Celery app configuration for TIMS."""
import logging
import os

from celery import Celery

logger = logging.getLogger(__name__)

# Default settings module for 'celery' CLI command
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school.settings.development')

app = Celery('school')

# Load settings from Django with CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks.py in each installed app
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Log task request via Django logging pipeline (not bare stdout)."""
    logger.debug('Request: %r', self.request)
