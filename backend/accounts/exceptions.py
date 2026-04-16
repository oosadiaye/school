"""Account-specific domain exceptions."""
from core.exceptions import DomainError


class InvalidCredentials(DomainError):
    """Wrong username or password."""

    status_code = 401
    error_code = 'invalid_credentials'


class InvalidToken(DomainError):
    """JWT token is expired, tampered, or otherwise invalid."""

    status_code = 401
    error_code = 'invalid_token'


class AccountDisabled(DomainError):
    """User account exists but is deactivated."""

    status_code = 403
    error_code = 'account_disabled'
