"""Tests for library service layer."""
import datetime
from decimal import Decimal

import pytest
from django.test import TestCase
from django.utils import timezone

from library.exceptions import AlreadyReserved, BookUnavailable, LoanNotActive
from library.models import Book, BookLoan, Reservation
from library.services import LoanService, ReservationService
from library.tests.factories import (
    BookFactory,
    BookLoanFactory,
    LibraryMemberFactory,
    ReservationFactory,
)


@pytest.mark.django_db
class TestLoanServiceBorrow(TestCase):
    """Tests for LoanService.borrow."""

    def test_borrow_decrements_available_copies(self):
        """Borrowing a book decrements available_copies by 1."""
        book = BookFactory(total_copies=3, available_copies=3)
        member = LibraryMemberFactory()

        LoanService.borrow(member=member, book=book)

        book.refresh_from_db()
        assert book.available_copies == 2

    def test_borrow_raises_when_no_copies_available(self):
        """Borrowing when available_copies == 0 raises BookUnavailable."""
        book = BookFactory(total_copies=1, available_copies=0)
        member = LibraryMemberFactory()

        with pytest.raises(BookUnavailable):
            LoanService.borrow(member=member, book=book)

    def test_borrow_sets_default_14_day_due_date(self):
        """When no due_date is provided, default is today + 14 days."""
        book = BookFactory(total_copies=3, available_copies=3)
        member = LibraryMemberFactory()

        loan = LoanService.borrow(member=member, book=book)

        expected = datetime.date.today() + datetime.timedelta(days=14)
        assert loan.due_date == expected

    def test_borrow_creates_loan_with_borrowed_status(self):
        """A new loan should have status 'borrowed'."""
        book = BookFactory(total_copies=2, available_copies=2)
        member = LibraryMemberFactory()

        loan = LoanService.borrow(member=member, book=book)

        assert loan.status == 'borrowed'
        assert loan.book_id == book.pk
        assert loan.member_id == member.pk


@pytest.mark.django_db
class TestLoanServiceReturn(TestCase):
    """Tests for LoanService.return_loan."""

    def test_return_calculates_overdue_fine(self):
        """Returning a book 5 days overdue yields fine of 250."""
        book = BookFactory(total_copies=3, available_copies=2)
        member = LibraryMemberFactory()
        loan = BookLoanFactory(
            book=book,
            member=member,
            due_date=datetime.date(2025, 1, 1),
            status='borrowed',
        )

        returned_loan = LoanService.return_loan(
            loan, returned_on=datetime.date(2025, 1, 6),
        )

        assert returned_loan.fine_amount == Decimal('250')
        assert returned_loan.status == 'returned'
        assert returned_loan.return_date == datetime.date(2025, 1, 6)

    def test_return_increments_available_copies(self):
        """Returning a book increments available_copies by 1."""
        book = BookFactory(total_copies=3, available_copies=1)
        member = LibraryMemberFactory()
        loan = BookLoanFactory(
            book=book,
            member=member,
            status='borrowed',
        )

        LoanService.return_loan(loan, returned_on=datetime.date.today())

        book.refresh_from_db()
        assert book.available_copies == 2

    def test_return_on_time_has_zero_fine(self):
        """Returning on or before due_date yields zero fine."""
        book = BookFactory(total_copies=3, available_copies=2)
        member = LibraryMemberFactory()
        due = datetime.date(2025, 6, 15)
        loan = BookLoanFactory(
            book=book, member=member, due_date=due, status='borrowed',
        )

        returned_loan = LoanService.return_loan(loan, returned_on=due)

        assert returned_loan.fine_amount == Decimal('0')

    def test_return_raises_if_already_returned(self):
        """Returning a loan that is already returned raises LoanNotActive."""
        loan = BookLoanFactory(status='returned')

        with pytest.raises(LoanNotActive):
            LoanService.return_loan(loan)


@pytest.mark.django_db
class TestLoanServiceOverdue(TestCase):
    """Tests for LoanService.list_overdue."""

    def test_list_overdue_returns_unreturned_past_due(self):
        """list_overdue returns loans past due that have not been returned."""
        past_due = datetime.date.today() - datetime.timedelta(days=5)
        future_due = datetime.date.today() + datetime.timedelta(days=5)

        overdue_loan = BookLoanFactory(due_date=past_due, status='borrowed')
        _not_overdue = BookLoanFactory(due_date=future_due, status='borrowed')
        _returned = BookLoanFactory(
            due_date=past_due, status='returned',
            return_date=datetime.date.today(),
        )

        result = list(LoanService.list_overdue())
        assert overdue_loan in result
        assert _not_overdue not in result
        assert _returned not in result


@pytest.mark.django_db
class TestReservationService(TestCase):
    """Tests for ReservationService."""

    def test_reserve_creates_active_reservation(self):
        """reserve() creates a reservation with status 'pending'."""
        book = BookFactory()
        member = LibraryMemberFactory()

        reservation = ReservationService.reserve(member=member, book=book)

        assert reservation.status == 'pending'
        assert reservation.book_id == book.pk
        assert reservation.member_id == member.pk

    def test_reserve_raises_if_already_reserved(self):
        """Duplicate pending reservation for same member+book raises AlreadyReserved."""
        book = BookFactory()
        member = LibraryMemberFactory()
        ReservationFactory(book=book, member=member, status='pending')

        with pytest.raises(AlreadyReserved):
            ReservationService.reserve(member=member, book=book)

    def test_reserve_allows_after_cancellation(self):
        """A cancelled reservation should not block a new reservation."""
        book = BookFactory()
        member = LibraryMemberFactory()
        ReservationFactory(book=book, member=member, status='cancelled')

        reservation = ReservationService.reserve(member=member, book=book)
        assert reservation.status == 'pending'

    def test_expire_old_marks_expired(self):
        """expire_old cancels pending reservations older than the threshold."""
        book = BookFactory()
        member = LibraryMemberFactory()

        old_res = ReservationFactory(book=book, member=member, status='pending')
        # Backdate created_at to 3 days ago
        Reservation.objects.filter(pk=old_res.pk).update(
            created_at=timezone.now() - datetime.timedelta(hours=72),
        )

        new_res = ReservationFactory(status='pending')

        count = ReservationService.expire_old(hours=48)

        old_res.refresh_from_db()
        new_res.refresh_from_db()

        assert count == 1
        assert old_res.status == 'expired'
        assert new_res.status == 'pending'

    def test_cancel_sets_cancelled_status(self):
        """cancel() sets reservation status to 'cancelled'."""
        reservation = ReservationFactory(status='pending')

        ReservationService.cancel(reservation)

        reservation.refresh_from_db()
        assert reservation.status == 'cancelled'
