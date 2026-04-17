"""Integration tests for hostel API endpoints."""
import pytest


@pytest.mark.django_db
def test_list_hostels(authed_admin_client):
    response = authed_admin_client.get('/api/hostel/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_create_hostel(api_client):
    """Write operations require auth even on IsAuthenticatedOrReadOnly views."""
    response = api_client.post('/api/hostel/', {})
    assert response.status_code in [401, 403]
