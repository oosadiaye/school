"""Shared pytest fixtures for all tests."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    """Unauthenticated DRF APIClient. Does not touch the database.

    Add the `db` marker or use a user-creating fixture if your test needs
    DB access.
    """
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Create a superuser with user_type='admin' for tests.

    Note: create_superuser sets is_superuser=True, which bypasses all Django
    permission checks. Tests that specifically need to verify admin-role
    permission logic (without superuser bypass) should create a regular user
    with user_type='admin' instead.
    """
    return User.objects.create_superuser(
        username='admin_test',
        email='admin@test.local',
        password='TestPass12345!',
        first_name='Admin',
        last_name='User',
        user_type='admin',
    )


@pytest.fixture
def student_user(db):
    """Create a regular student user for tests."""
    return User.objects.create_user(
        username='student_test',
        email='student@test.local',
        password='TestPass12345!',
        first_name='Student',
        last_name='User',
        user_type='student',
    )


@pytest.fixture
def authed_admin_client(api_client, admin_user):
    """APIClient authenticated as admin user."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def authed_student_client(api_client, student_user):
    """APIClient authenticated as student user."""
    api_client.force_authenticate(user=student_user)
    return api_client
