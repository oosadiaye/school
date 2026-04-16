"""Tests for Celery infrastructure via a simple ping task."""
import pytest
from core.tasks import ping


def test_ping_task_runs_synchronously_via_apply():
    """Confirm Celery task can be invoked (sync mode for tests)."""
    result = ping.apply(args=['hello']).get()
    assert result == 'pong: hello'


def test_ping_task_is_registered():
    """Confirm Celery app sees the task."""
    from school.celery import app
    assert 'core.tasks.ping' in app.tasks
