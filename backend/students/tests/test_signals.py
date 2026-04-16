"""Tests for student signals."""
import pytest
from students.tests.factories import StudentFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_student_creation_creates_welcome_notification():
    """New student gets a welcome notification."""
    student = StudentFactory()
    notif = Notification.objects.filter(user=student.user, title='Welcome to TIMS')
    assert notif.exists()
    assert student.matric_number in notif.first().message


@pytest.mark.django_db
def test_student_update_does_not_create_duplicate_notification():
    """Updating a student doesn't fire the created-only signal."""
    student = StudentFactory()
    initial_count = Notification.objects.filter(user=student.user).count()
    student.level = 200
    student.save()
    assert Notification.objects.filter(user=student.user).count() == initial_count


@pytest.mark.django_db
def test_student_creation_attempts_invoice_generation():
    """Signal attempts invoice generation (may create 0 if no fee structures match)."""
    # This test verifies the signal doesn't crash even without matching fee structures
    student = StudentFactory()  # Should not raise
    assert student.pk is not None
