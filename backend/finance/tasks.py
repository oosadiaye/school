"""Celery periodic tasks for the finance app."""
from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def check_overdue_invoices():
    """Flag overdue invoices and create reminder notifications. Runs daily 8 AM."""
    from finance.services import InvoiceService
    from notifications.services import NotificationService

    overdue = InvoiceService.list_overdue()
    count = 0
    for invoice in overdue.select_related('student__user', 'fee_structure__fee_type'):
        if invoice.status != 'overdue':
            invoice.status = 'overdue'
            invoice.save(update_fields=['status'])

        NotificationService.create(
            user=invoice.student.user,
            level='warning',
            title='Invoice Overdue',
            message=(
                f'Your invoice of \u20a6{invoice.amount:,.2f} for '
                f'{invoice.fee_structure.fee_type.name} is overdue. '
                f'Due date: {invoice.due_date}.'
            ),
        )
        count += 1

    logger.info("Processed %d overdue invoices", count)
    return f'{count} overdue invoices processed'


@shared_task
def send_payment_reminders():
    """Send reminders for invoices due within 7 days. Runs Monday 9 AM."""
    from datetime import timedelta

    from django.utils import timezone

    from finance.models import Invoice
    from notifications.services import NotificationService

    upcoming_due = Invoice.objects.filter(
        status__in=['pending', 'partially_paid'],
        due_date__lte=timezone.now().date() + timedelta(days=7),
        due_date__gte=timezone.now().date(),
    ).select_related('student__user', 'fee_structure__fee_type')

    count = 0
    for invoice in upcoming_due:
        NotificationService.create(
            user=invoice.student.user,
            level='info',
            title='Payment Reminder',
            message=(
                f'Your invoice of \u20a6{invoice.balance:,.2f} for '
                f'{invoice.fee_structure.fee_type.name} is due on '
                f'{invoice.due_date}.'
            ),
        )
        count += 1

    logger.info("Sent %d payment reminders", count)
    return f'{count} payment reminders sent'
