"""Tests for HR signals."""
import pytest
from hr.tests.factories import LeaveRequestFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_approved_leave_creates_notification():
    """Approved leave request triggers a notification to the employee."""
    leave = LeaveRequestFactory(status='approved')
    assert Notification.objects.filter(
        user=leave.employee.user,
        title='Leave Approved',
    ).exists()


@pytest.mark.django_db
def test_pending_leave_does_not_notify():
    """Pending leave request does not trigger a notification."""
    leave = LeaveRequestFactory(status='pending')
    assert not Notification.objects.filter(
        user=leave.employee.user,
        title='Leave Approved',
    ).exists()
