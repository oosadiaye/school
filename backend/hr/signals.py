"""Signals for the HR app -- fires on leave request lifecycle events."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LeaveRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=LeaveRequest)
def on_leave_approved(sender, instance, **kwargs):
    """Notify employee when their leave request is approved."""
    if instance.status != 'approved':
        return
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.employee.user,
            level='success',
            title='Leave Approved',
            message=(
                f'Your {instance.leave_type.name} leave '
                f'({instance.start_date} to {instance.end_date}) has been approved.'
            ),
        )
    except Exception:
        logger.exception("Failed to notify on leave approval for %s", instance.pk)
