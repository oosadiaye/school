"""Tests for Celery infrastructure via a simple ping task."""
import pytest

from core.tasks import ping
from school.celery import app


def test_ping_task_runs_synchronously_via_apply():
    """Confirm Celery task can be invoked with an explicit payload (sync mode for tests)."""
    result = ping.apply(args=['hello']).get()
    assert result == 'pong: hello'


def test_ping_task_uses_default_payload():
    """Confirm the default argument path returns the expected value without args."""
    result = ping.apply().get()
    assert result == 'pong: hello'


def test_ping_task_is_registered():
    """Confirm Celery app's autodiscover sees the task."""
    assert 'core.tasks.ping' in app.tasks


@pytest.mark.django_db
def test_celery_beat_schedule_tasks_are_registered():
    """Every task referenced in CELERY_BEAT_SCHEDULE must be in the registry."""
    from django.conf import settings

    # Force lazy autodiscovery so all task modules are loaded.
    app.autodiscover_tasks(force=True)
    app.loader.import_default_modules()

    for name, config in settings.CELERY_BEAT_SCHEDULE.items():
        task_name = config['task']
        assert task_name in app.tasks, f"Task '{task_name}' not found in Celery registry"
