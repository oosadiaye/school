"""Signals for the finance app -- fires on payment lifecycle events."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Payment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Payment)
def on_payment_completed(sender, instance, **kwargs):
    """Notify student when a payment is completed."""
    if instance.status != 'completed':
        return
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.student.user,
            level='success',
            title='Payment Confirmed',
            message=f'Payment of \u20a6{instance.amount:,.2f} has been confirmed.',
        )
    except Exception:
        logger.exception("Failed to notify on payment completion for %s", instance.pk)
