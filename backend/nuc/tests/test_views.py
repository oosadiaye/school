"""Integration tests for NUC API endpoints."""
import pytest


@pytest.mark.django_db
def test_list_accreditations(authed_admin_client):
    response = authed_admin_client.get('/api/nuc/accreditations/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_create_accreditation(api_client):
    """Write operations require auth even on IsAuthenticatedOrReadOnly views."""
    response = api_client.post('/api/nuc/accreditations/', {})
    assert response.status_code in [401, 403]
