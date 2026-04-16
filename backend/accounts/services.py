"""Business logic for accounts: authentication and user management."""
from __future__ import annotations

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from accounts.authentication import generate_token, generate_refresh_token
from accounts.exceptions import InvalidCredentials, InvalidToken, AccountDisabled
from core.exceptions import ValidationFailed

User = get_user_model()


class AuthService:
    """Handles login, token refresh, and password changes."""

    @staticmethod
    def login(username: str, password: str) -> dict:
        """Authenticate user and return JWT tokens plus user info.

        Raises:
            InvalidCredentials: wrong username or password.
            AccountDisabled: user exists but is_active is False.
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise InvalidCredentials('Invalid username or password.')

        if not user.is_active:
            raise AccountDisabled('This account has been deactivated.')

        if not user.check_password(password):
            raise InvalidCredentials('Invalid username or password.')

        access_token = generate_token(user)
        refresh_token = generate_refresh_token(user)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Decode a refresh token and issue a new access token.

        Raises:
            InvalidToken: token expired, tampered, or user not found.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256'],
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidToken('Refresh token is invalid or expired.')

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise InvalidToken('User for this token no longer exists.')

        access_token = generate_token(user)
        return {'access_token': access_token}

    @staticmethod
    def change_password(user, old_password: str, new_password: str) -> None:
        """Verify old password and set a new one.

        Raises:
            InvalidCredentials: old password is wrong.
            ValidationFailed: new password fails Django validators.
        """
        if not user.check_password(old_password):
            raise InvalidCredentials('Current password is incorrect.')

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            raise ValidationFailed(
                'New password does not meet requirements.',
                details={'password': list(exc.messages)},
            )

        user.set_password(new_password)
        user.save(update_fields=['password'])


class UserService:
    """Handles user creation and lifecycle operations."""

    @staticmethod
    def create_user(data: dict, created_by=None) -> User:
        """Create a new user from validated data.

        Uses create_superuser for admin user_type, create_user otherwise.
        """
        user_type = data.get('user_type', 'student')
        if user_type == 'admin':
            return User.objects.create_superuser(**data)
        return User.objects.create_user(**data)

    @staticmethod
    def deactivate_user(user, by=None) -> User:
        """Deactivate a user account.

        Returns the updated user instance.
        """
        user.is_active = False
        user.save(update_fields=['is_active'])
        return user
