"""Celery tasks for the HR module."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def daily_attendance_summary():
    """Generate daily attendance summary. Runs weekdays 6 PM."""
    logger.info("Daily attendance summary task executed")
    # Placeholder -- Phase 4+ will add real summary email to HODs
    return 'Attendance summary completed'
