"""Integration tests for HR API endpoints."""
import pytest


@pytest.mark.django_db
def test_list_employees(authed_admin_client):
    response = authed_admin_client.get('/api/hr/employees/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_access_hr_employees(api_client):
    """Employee list requires authentication."""
    response = api_client.post('/api/hr/employees/', {})
    assert response.status_code in [401, 403]
