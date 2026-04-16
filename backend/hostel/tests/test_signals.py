"""Tests for hostel signals."""
import pytest
from hostel.tests.factories import HostelAssignmentFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_new_assignment_creates_notification():
    """New hostel assignment triggers a notification to the student."""
    assignment = HostelAssignmentFactory()
    assert Notification.objects.filter(
        user=assignment.student.user,
        title='Room Assigned',
    ).exists()


@pytest.mark.django_db
def test_updated_assignment_does_not_notify():
    """Updating an existing assignment does not create a duplicate notification."""
    assignment = HostelAssignmentFactory()
    initial_count = Notification.objects.filter(
        user=assignment.student.user,
        title='Room Assigned',
    ).count()
    assignment.status = 'checked_in'
    assignment.save()
    assert Notification.objects.filter(
        user=assignment.student.user,
        title='Room Assigned',
    ).count() == initial_count
