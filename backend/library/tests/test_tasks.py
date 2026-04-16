"""Tests for library Celery tasks."""
from __future__ import annotations

import datetime

import pytest
from django.utils import timezone

from library.tasks import check_overdue_books, expire_old_reservations
from library.tests.factories import BookLoanFactory, ReservationFactory
from notifications.models import Notification


@pytest.mark.django_db
class TestCheckOverdueBooks:
    def test_notifies_overdue_loans(self):
        """Overdue book loans trigger a warning notification to the member."""
        loan = BookLoanFactory(
            due_date=datetime.date.today() - datetime.timedelta(days=3),
            status='borrowed',
        )
        result = check_overdue_books.apply().get()

        assert Notification.objects.filter(
            user=loan.member.user,
            title='Book Overdue',
        ).exists()
        assert '1 overdue book loans processed' in result

    def test_no_overdue_returns_zero(self):
        """When no loans are overdue, count is 0."""
        BookLoanFactory(
            due_date=datetime.date.today() + datetime.timedelta(days=7),
            status='borrowed',
        )
        result = check_overdue_books.apply().get()
        assert result == '0 overdue book loans processed'


@pytest.mark.django_db
class TestExpireOldReservations:
    def test_expires_old_reservations(self):
        """Reservations older than 48 hours are marked expired."""
        reservation = ReservationFactory(status='pending')
        # Backdate the created_at to > 48 hours ago
        from library.models import Reservation
        Reservation.objects.filter(pk=reservation.pk).update(
            created_at=timezone.now() - datetime.timedelta(hours=72),
        )

        result = expire_old_reservations.apply().get()

        reservation.refresh_from_db()
        assert reservation.status == 'expired'
        assert '1 reservations expired' in result

    def test_keeps_recent_reservations(self):
        """Recent reservations (< 48h) should not be expired."""
        ReservationFactory(status='pending')
        result = expire_old_reservations.apply().get()
        assert result == '0 reservations expired'
