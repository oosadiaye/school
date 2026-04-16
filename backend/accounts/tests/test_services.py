"""Tests for accounts service layer."""
import pytest
from accounts.services import AuthService, UserService
from accounts.exceptions import InvalidCredentials, InvalidToken, AccountDisabled
from accounts.tests.factories import UserFactory, AdminFactory


@pytest.mark.django_db
def test_login_returns_tokens_for_valid_credentials():
    user = UserFactory(username='logintest')
    result = AuthService.login('logintest', 'TestPass12345!')
    assert 'access_token' in result
    assert 'refresh_token' in result
    assert result['user']['username'] == 'logintest'


@pytest.mark.django_db
def test_login_raises_invalid_credentials_on_wrong_password():
    UserFactory(username='wrongpass')
    with pytest.raises(InvalidCredentials):
        AuthService.login('wrongpass', 'WRONG')


@pytest.mark.django_db
def test_login_raises_invalid_credentials_on_nonexistent_user():
    with pytest.raises(InvalidCredentials):
        AuthService.login('nonexistent', 'anything')


@pytest.mark.django_db
def test_login_raises_account_disabled_when_inactive():
    UserFactory(username='inactive', is_active=False)
    with pytest.raises(AccountDisabled):
        AuthService.login('inactive', 'TestPass12345!')


@pytest.mark.django_db
def test_refresh_access_token_returns_new_token():
    user = UserFactory(username='refreshtest')
    tokens = AuthService.login('refreshtest', 'TestPass12345!')
    result = AuthService.refresh_access_token(tokens['refresh_token'])
    assert 'access_token' in result


@pytest.mark.django_db
def test_refresh_raises_invalid_token_on_expired():
    with pytest.raises(InvalidToken):
        AuthService.refresh_access_token('totally.bogus.token')


@pytest.mark.django_db
def test_change_password_verifies_old_password():
    user = UserFactory(username='chgpass')
    with pytest.raises(InvalidCredentials):
        AuthService.change_password(user, 'WRONGOLD', 'NewValidPass12!')


@pytest.mark.django_db
def test_change_password_succeeds_with_correct_old():
    user = UserFactory(username='chgpass2')
    AuthService.change_password(user, 'TestPass12345!', 'NewValidPass12!')
    user.refresh_from_db()
    assert user.check_password('NewValidPass12!')
