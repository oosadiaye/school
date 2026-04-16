"""Tests for library signals."""
from decimal import Decimal

import pytest
from library.tests.factories import BookLoanFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_returned_with_fine_creates_notification():
    """Returned book with a fine triggers a notification to the member."""
    loan = BookLoanFactory(status='returned', fine_amount=Decimal('500.00'))
    assert Notification.objects.filter(
        user=loan.member.user,
        title='Book Return \u2014 Fine Applied',
    ).exists()


@pytest.mark.django_db
def test_returned_without_fine_does_not_notify():
    """Returned book without a fine does not trigger a notification."""
    loan = BookLoanFactory(status='returned', fine_amount=Decimal('0.00'))
    assert not Notification.objects.filter(
        user=loan.member.user,
        title='Book Return \u2014 Fine Applied',
    ).exists()


@pytest.mark.django_db
def test_borrowed_status_does_not_notify():
    """Borrowed book does not trigger a fine notification."""
    loan = BookLoanFactory(status='borrowed', fine_amount=Decimal('500.00'))
    assert not Notification.objects.filter(
        user=loan.member.user,
        title='Book Return \u2014 Fine Applied',
    ).exists()
