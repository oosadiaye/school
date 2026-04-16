"""Tests for academic signals."""
import pytest
from academic.tests.factories import ResultFactory
from notifications.models import Notification


@pytest.mark.django_db
def test_result_published_creates_notification():
    """Published result triggers a notification to the student."""
    result = ResultFactory(is_published=True)
    assert Notification.objects.filter(
        user=result.student.user,
        title='Result Published',
    ).exists()


@pytest.mark.django_db
def test_result_unpublished_does_not_notify():
    """Unpublished result does not trigger a notification."""
    result = ResultFactory(is_published=False)
    assert not Notification.objects.filter(
        user=result.student.user,
        title='Result Published',
    ).exists()
