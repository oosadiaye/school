"""Integration tests for notifications API endpoints."""
import pytest


@pytest.mark.django_db
def test_list_notifications_requires_auth(api_client):
    """Notifications list requires authentication."""
    response = api_client.get('/api/notifications/')
    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_list_notifications_as_admin(authed_admin_client):
    response = authed_admin_client.get('/api/notifications/')
    assert response.status_code == 200
