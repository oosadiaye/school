"""Shared Celery tasks for the core app."""
from celery import shared_task


@shared_task
def ping(payload: str = 'hello') -> str:
    """Sanity check task — returns the input with a pong prefix."""
    return f'pong: {payload}'
