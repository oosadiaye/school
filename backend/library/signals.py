"""Signals for the library app -- fires on book loan lifecycle events."""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import BookLoan

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BookLoan)
def on_book_returned_with_fine(sender, instance, **kwargs):
    """Notify member when a returned book incurs a fine."""
    if instance.status != 'returned' or not instance.fine_amount or instance.fine_amount <= 0:
        return
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.member.user,
            level='warning',
            title='Book Return \u2014 Fine Applied',
            message=(
                f'Fine of \u20a6{instance.fine_amount:,.2f} applied for '
                f'overdue return of "{instance.book.title}".'
            ),
        )
    except Exception:
        logger.exception("Failed to notify on book return fine for %s", instance.pk)
