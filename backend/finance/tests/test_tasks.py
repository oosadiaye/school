"""Tests for finance Celery tasks."""
from __future__ import annotations

import datetime

import pytest
from finance.tasks import check_overdue_invoices, send_payment_reminders
from finance.tests.factories import InvoiceFactory
from notifications.models import Notification


@pytest.mark.django_db
class TestCheckOverdueInvoices:
    def test_flags_and_notifies(self):
        """Overdue invoices get status='overdue' and a notification is created."""
        invoice = InvoiceFactory(
            due_date=datetime.date.today() - datetime.timedelta(days=5),
            status='pending',
        )
        result = check_overdue_invoices.apply().get()

        invoice.refresh_from_db()
        assert invoice.status == 'overdue'
        assert Notification.objects.filter(
            user=invoice.student.user,
            title='Invoice Overdue',
        ).exists()
        assert '1 overdue invoices processed' in result

    def test_handles_partially_paid_overdue(self):
        """Partially-paid overdue invoices also get flagged and notified."""
        invoice = InvoiceFactory(
            due_date=datetime.date.today() - datetime.timedelta(days=3),
            status='pending',
        )
        # Force status to partially_paid (still picked up by list_overdue)
        from finance.models import Invoice
        Invoice.objects.filter(pk=invoice.pk).update(status='partially_paid')

        result = check_overdue_invoices.apply().get()

        invoice.refresh_from_db()
        assert invoice.status == 'overdue'
        assert Notification.objects.filter(
            user=invoice.student.user, title='Invoice Overdue',
        ).count() == 1
        assert '1 overdue invoices processed' in result

    def test_no_overdue_returns_zero(self):
        """When no invoices are overdue, count is 0."""
        InvoiceFactory(
            due_date=datetime.date.today() + datetime.timedelta(days=10),
            status='pending',
        )
        result = check_overdue_invoices.apply().get()
        assert result == '0 overdue invoices processed'


@pytest.mark.django_db
class TestSendPaymentReminders:
    def test_creates_notifications_for_upcoming(self):
        """Invoices due within 7 days get a payment reminder notification."""
        invoice = InvoiceFactory(
            due_date=datetime.date.today() + datetime.timedelta(days=3),
            status='pending',
        )
        result = send_payment_reminders.apply().get()

        assert Notification.objects.filter(
            user=invoice.student.user,
            title='Payment Reminder',
        ).exists()
        assert '1 payment reminders sent' in result

    def test_ignores_invoices_due_beyond_7_days(self):
        """Invoices due more than 7 days out should not get reminders."""
        InvoiceFactory(
            due_date=datetime.date.today() + datetime.timedelta(days=14),
            status='pending',
        )
        result = send_payment_reminders.apply().get()
        assert result == '0 payment reminders sent'
