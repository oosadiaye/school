"""Integration tests for auth API endpoints."""
import pytest
from accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_login_endpoint_returns_tokens(api_client):
    UserFactory(username='loginview')
    response = api_client.post('/api/accounts/auth/login/', {
        'username': 'loginview', 'password': 'TestPass12345!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.data
    assert 'refresh_token' in response.data


@pytest.mark.django_db
def test_login_endpoint_rejects_wrong_password(api_client):
    UserFactory(username='badlogin')
    response = api_client.post('/api/accounts/auth/login/', {
        'username': 'badlogin', 'password': 'WRONG'
    })
    assert response.status_code == 401
    assert response.data['error'] == 'invalid_credentials'


@pytest.mark.django_db
def test_me_endpoint_requires_auth(api_client):
    response = api_client.get('/api/accounts/users/me/')
    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_me_endpoint_returns_profile(authed_admin_client):
    response = authed_admin_client.get('/api/accounts/users/me/')
    assert response.status_code == 200
    assert 'username' in response.data


@pytest.mark.django_db
def test_change_password_via_endpoint(authed_admin_client, admin_user):
    response = authed_admin_client.post('/api/accounts/users/change_password/', {
        'old_password': 'TestPass12345!',
        'new_password': 'NewValidPass12!',
        'new_password_confirm': 'NewValidPass12!',
    })
    assert response.status_code == 200
