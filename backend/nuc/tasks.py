"""Celery periodic tasks for the NUC app."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_expiring_accreditations():
    """Alert admins about accreditations expiring within 90 days. Runs Monday 8 AM."""
    from django.contrib.auth import get_user_model

    from notifications.services import NotificationService
    from nuc.services import AccreditationService

    User = get_user_model()
    expiring = AccreditationService.list_expiring(within_days=90)
    admin_users = User.objects.filter(user_type='admin', is_active=True)

    count = 0
    for accreditation in expiring:
        for admin in admin_users:
            NotificationService.create(
                user=admin,
                level='warning',
                title='Accreditation Expiring',
                message=(
                    f'{accreditation.programme.name} accreditation expires on '
                    f'{accreditation.expiry_date}.'
                ),
            )
            count += 1

    logger.info("Sent %d accreditation expiry alerts", count)
    return f'{count} accreditation alerts sent'
