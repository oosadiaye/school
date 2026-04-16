"""Signals for the hostel app -- fires on room assignment events."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import HostelAssignment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=HostelAssignment)
def on_room_assigned(sender, instance, created, **kwargs):
    """Notify student when they are assigned a hostel room."""
    if not created:
        return
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.student.user,
            level='success',
            title='Room Assigned',
            message=(
                f'You have been assigned to {instance.room.hostel.name}, '
                f'Room {instance.room.room_number}.'
            ),
        )
    except Exception:
        logger.exception("Failed to notify on room assignment for %s", instance.pk)
