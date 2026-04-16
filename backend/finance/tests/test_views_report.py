"""Tests for finance reports endpoints."""
import pytest


@pytest.mark.django_db
def test_waivers_report_does_not_crash(authed_admin_client):
    """waivers_report must not raise NameError for undefined `total_waivered`."""
    response = authed_admin_client.get('/api/finance/reports/waivers_report/')
    assert response.status_code == 200
    data = response.json()
    assert 'total_waivers' in data
    assert 'total_amount_waived' in data
    assert 'pending_waivers' in data
    assert data['total_amount_waived'] == 0  # no waivers in test DB
