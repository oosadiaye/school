"""Integration tests for library API endpoints."""
import pytest


@pytest.mark.django_db
def test_list_books(authed_admin_client):
    response = authed_admin_client.get('/api/library/books/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_create_book(api_client):
    """Write operations require auth even on IsAuthenticatedOrReadOnly views."""
    response = api_client.post('/api/library/books/', {})
    assert response.status_code in [401, 403]
