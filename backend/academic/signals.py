"""Signals for the academic app -- fires on result and session lifecycle events."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Result

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Result)
def on_result_published(sender, instance, **kwargs):
    """Notify student when their result is published."""
    if not instance.is_published:
        return
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.student.user,
            level='info',
            title='Result Published',
            message=f'Your result for {instance.course.name} has been published.',
        )
    except Exception:
        logger.exception("Failed to notify on result publish for %s", instance.pk)
