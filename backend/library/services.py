"""Business logic for the library app."""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models import F, QuerySet
from django.utils import timezone

from library.exceptions import AlreadyReserved, BookUnavailable, LoanNotActive
from library.models import Book, BookLoan, LibraryMember, Reservation

FINE_PER_DAY = Decimal('50')
DEFAULT_LOAN_DAYS = 14


class BookService:
    """Handles book creation and availability management."""

    @staticmethod
    def create_book(data: dict, by=None) -> Book:
        """Create a book with available_copies set to total_copies."""
        total = data.get('total_copies', 1)
        data['available_copies'] = total
        book = Book.objects.create(**data)
        return book

    @staticmethod
    def update_availability(book: Book, delta: int) -> None:
        """Atomically increment or decrement available_copies."""
        Book.objects.filter(pk=book.pk).update(
            available_copies=F('available_copies') + delta,
        )
        book.refresh_from_db()


class LoanService:
    """Handles borrowing, returning, and overdue tracking."""

    @staticmethod
    @transaction.atomic
    def borrow(
        member: LibraryMember,
        book: Book,
        due_date: Optional[datetime.date] = None,
        by=None,
    ) -> BookLoan:
        """Borrow a book for a member.

        Decrements available_copies atomically and creates a BookLoan record.

        Raises:
            BookUnavailable: if the book has no available copies.
        """
        # Lock the book row to prevent race conditions
        book = Book.objects.select_for_update().get(pk=book.pk)
        if book.available_copies <= 0:
            raise BookUnavailable(
                f"No available copies of '{book.title}'"
            )

        Book.objects.filter(pk=book.pk).update(
            available_copies=F('available_copies') - 1,
        )

        if due_date is None:
            due_date = datetime.date.today() + datetime.timedelta(days=DEFAULT_LOAN_DAYS)

        loan = BookLoan.objects.create(
            book=book,
            member=member,
            due_date=due_date,
            status='borrowed',
        )
        return loan

    @staticmethod
    @transaction.atomic
    def return_loan(
        loan: BookLoan,
        returned_on: Optional[datetime.date] = None,
        by=None,
    ) -> BookLoan:
        """Return a borrowed book.

        Calculates overdue fine, sets return_date, and increments
        available_copies atomically.

        Raises:
            LoanNotActive: if the loan is not in 'borrowed' or 'overdue' status.
        """
        if loan.status not in ('borrowed', 'overdue'):
            raise LoanNotActive(
                f"Loan {loan.pk} is not active (status: {loan.status})"
            )

        if returned_on is None:
            returned_on = datetime.date.today()

        fine = LoanService.calculate_overdue_fine(loan, as_of=returned_on)

        loan.return_date = returned_on
        loan.fine_amount = fine
        loan.status = 'returned'
        loan.save()

        Book.objects.filter(pk=loan.book_id).update(
            available_copies=F('available_copies') + 1,
        )

        return loan

    @staticmethod
    def calculate_overdue_fine(
        loan: BookLoan,
        as_of: Optional[datetime.date] = None,
    ) -> Decimal:
        """Calculate the overdue fine for a loan.

        Returns days_overdue * 50 as a Decimal.
        """
        if as_of is None:
            as_of = datetime.date.today()
        days_overdue = max(0, (as_of - loan.due_date).days)
        return Decimal(days_overdue) * FINE_PER_DAY

    @staticmethod
    def list_overdue() -> QuerySet[BookLoan]:
        """Return loans that are currently overdue (not returned, past due)."""
        today = datetime.date.today()
        return BookLoan.objects.filter(
            return_date__isnull=True,
            due_date__lt=today,
        )


class ReservationService:
    """Handles book reservations."""

    @staticmethod
    def reserve(
        member: LibraryMember,
        book: Book,
        by=None,
    ) -> Reservation:
        """Create a reservation for a member.

        Raises:
            AlreadyReserved: if an active (pending) reservation already exists.
        """
        exists = Reservation.objects.filter(
            member=member,
            book=book,
            status='pending',
        ).exists()
        if exists:
            raise AlreadyReserved(
                f"Member {member.pk} already has an active reservation for '{book.title}'"
            )

        return Reservation.objects.create(
            book=book,
            member=member,
            status='pending',
        )

    @staticmethod
    def cancel(reservation: Reservation, by=None) -> None:
        """Cancel a reservation."""
        reservation.status = 'cancelled'
        reservation.save()

    @staticmethod
    def expire_old(hours: int = 48) -> int:
        """Expire pending reservations older than *hours*.

        Returns the count of expired reservations.
        """
        cutoff = timezone.now() - datetime.timedelta(hours=hours)
        count = Reservation.objects.filter(
            status='pending',
            created_at__lt=cutoff,
        ).update(status='expired')
        return count
