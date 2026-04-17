"""Celery tasks for sending emails and SMS."""
import logging

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, to, subject, body_text, body_html=None):
    """Send a single email via Django's configured email backend."""
    try:
        from django.core.mail import send_mail

        send_mail(
            subject=subject,
            message=body_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            html_message=body_html,
            fail_silently=False,
        )
        logger.info("Email sent to %s: %s", to, subject)
    except Exception as exc:
        logger.exception("Failed to send email to %s", to)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, to_phone, message):
    """Send SMS via configured provider. Placeholder -- logs for now."""
    logger.info("SMS to %s: %s", to_phone, message)
    # Phase 10 will add real SMS gateway integration (Termii/Africa's Talking)
    return f'SMS queued for {to_phone}'
