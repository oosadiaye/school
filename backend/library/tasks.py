"""Celery periodic tasks for the library app."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_books():
    """Check for overdue book loans and notify members. Runs daily 7 AM."""
    from library.services import LoanService
    from notifications.services import NotificationService

    overdue_loans = LoanService.list_overdue().select_related('member__user', 'book')
    count = 0
    for loan in overdue_loans:
        fine = LoanService.calculate_overdue_fine(loan)
        NotificationService.create(
            user=loan.member.user,
            level='warning',
            title='Book Overdue',
            message=(
                f'"{loan.book.title}" is overdue. Current fine: '
                f'\u20a6{fine:,.2f}. Please return it immediately.'
            ),
        )
        count += 1

    logger.info("Processed %d overdue book loans", count)
    return f'{count} overdue book loans processed'


@shared_task
def expire_old_reservations():
    """Cancel reservations older than 48 hours. Runs every 6 hours."""
    from library.services import ReservationService

    count = ReservationService.expire_old(hours=48)
    logger.info("Expired %d old reservations", count)
    return f'{count} reservations expired'
