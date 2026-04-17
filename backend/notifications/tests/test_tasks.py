"""Tests for notification Celery tasks."""
import pytest


@pytest.mark.django_db
def test_send_email_task_calls_send_mail(mocker):
    """Email task delegates to Django send_mail."""
    mock_send = mocker.patch('django.core.mail.send_mail')
    from notifications.tasks import send_email_task

    send_email_task.apply(args=['test@example.com', 'Subject', 'Body']).get()
    mock_send.assert_called_once()


def test_send_sms_task_returns_confirmation():
    """SMS task returns a confirmation string."""
    from notifications.tasks import send_sms_task

    result = send_sms_task.apply(args=['+2341234567890', 'Hello']).get()
    assert 'SMS queued' in result
