"""Smoke tests confirming pytest + Django wiring works."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_can_create_user(admin_user):
    """Verify DB fixture wiring: User model is writable and custom fields persist."""
    assert admin_user.pk is not None, "User fixture did not persist to DB"
    assert admin_user.username == 'admin_test'
    assert admin_user.user_type == 'admin'
    assert admin_user.is_superuser is True


@pytest.mark.django_db
def test_authed_client_works(authed_admin_client):
    """Admin client can hit a protected endpoint (uses reverse() for refactor safety)."""
    url = reverse('users-me')
    response = authed_admin_client.get(url)
    assert response.status_code == 200
