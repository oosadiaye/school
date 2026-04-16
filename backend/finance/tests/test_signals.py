"""Tests for finance signals."""
import pytest
from finance.tests.factories import PaymentFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_completed_payment_creates_notification():
    """Completed payment triggers a notification to the student."""
    payment = PaymentFactory(status='completed')
    assert Notification.objects.filter(
        user=payment.student.user,
        title='Payment Confirmed',
    ).exists()


@pytest.mark.django_db
def test_pending_payment_does_not_notify():
    """Pending payment does not trigger a notification."""
    payment = PaymentFactory(status='pending')
    assert not Notification.objects.filter(
        user=payment.student.user,
        title='Payment Confirmed',
    ).exists()
