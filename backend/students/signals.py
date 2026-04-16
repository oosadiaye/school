"""Signals for the students app -- fires on student lifecycle events."""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Student)
def on_student_created(sender, instance, created, **kwargs):
    """When a new student is created, generate invoices and send welcome notification."""
    if not created:
        return

    # 1. Auto-generate invoices for the student's session
    try:
        from academic.models import AcademicSession
        from finance.services import InvoiceService

        # Find session matching admission year
        session = AcademicSession.objects.filter(
            is_current=True
        ).first()

        if session:
            invoices = InvoiceService.generate_for_student(instance, session.name)
            logger.info(
                "Auto-generated %d invoices for new student %s",
                len(invoices) if isinstance(invoices, list) else 0,
                instance.matric_number,
            )
    except Exception:
        logger.exception("Failed to auto-generate invoices for student %s", instance.matric_number)

    # 2. Create welcome notification
    try:
        from notifications.services import NotificationService

        NotificationService.create(
            user=instance.user,
            level='success',
            title='Welcome to TIMS',
            message=f'Your registration is complete. Matric number: {instance.matric_number}',
        )
    except Exception:
        logger.exception("Failed to create welcome notification for student %s", instance.matric_number)
