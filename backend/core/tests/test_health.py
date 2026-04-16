"""Tests for health check endpoint."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_returns_200(client):
    """Health endpoint responds 200 OK with status JSON."""
    url = reverse('core:health')
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    assert 'checks' in data
    assert data['checks']['database'] is True


@pytest.mark.django_db
def test_health_endpoint_includes_redis_check(client):
    """Health endpoint reports redis connectivity status."""
    url = reverse('core:health')
    response = client.get(url)
    data = response.json()
    assert 'redis' in data['checks']
