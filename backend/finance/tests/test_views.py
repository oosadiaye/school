"""Integration tests for finance API endpoints."""
import pytest


@pytest.mark.django_db
def test_waivers_report_endpoint(authed_admin_client):
    """Regression test for the Phase 1 bug fix."""
    response = authed_admin_client.get('/api/finance/reports/waivers_report/')
    assert response.status_code == 200
    assert 'total_amount_waived' in response.data


@pytest.mark.django_db
def test_finance_summary_endpoint(authed_admin_client):
    response = authed_admin_client.get('/api/finance/reports/summary/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_list_invoices_as_admin(authed_admin_client):
    response = authed_admin_client.get('/api/finance/invoices/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_unauthenticated_cannot_access_finance_invoices(api_client):
    response = api_client.get('/api/finance/invoices/')
    assert response.status_code in [401, 403]
