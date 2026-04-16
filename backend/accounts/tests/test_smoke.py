"""Smoke tests confirming pytest + Django wiring works."""
import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_can_create_user(admin_user):
    """Admin fixture creates a valid user."""
    User = get_user_model()
    assert User.objects.filter(username='admin_test').exists()
    assert admin_user.user_type == 'admin'


@pytest.mark.django_db
def test_authed_client_works(authed_admin_client):
    """Admin client can hit a protected endpoint."""
    response = authed_admin_client.get('/api/accounts/users/me/')
    assert response.status_code == 200
