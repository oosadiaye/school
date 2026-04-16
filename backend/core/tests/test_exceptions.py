"""Tests for the custom DRF exception handler + domain error hierarchy."""
import pytest
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.exceptions import (
    DomainError,
    ValidationFailed,
    ConflictError,
    NotFound as DomainNotFound,
    PermissionDenied as DomainPermissionDenied,
    custom_exception_handler,
)


@pytest.fixture
def rf():
    return APIRequestFactory()


def _call_handler(exc, request=None):
    """Invoke our custom handler with a dummy DRF context."""
    context = {'view': None, 'request': request, 'args': (), 'kwargs': {}}
    return custom_exception_handler(exc, context)


def test_validation_failed_returns_400_with_standard_json():
    response = _call_handler(ValidationFailed("Field invalid", details={'field': 'name'}))
    assert response.status_code == 400
    assert response.data['error'] == 'validation_failed'
    assert response.data['message'] == 'Field invalid'
    assert response.data['details'] == {'field': 'name'}


def test_conflict_error_returns_409():
    response = _call_handler(ConflictError("Already exists"))
    assert response.status_code == 409
    assert response.data['error'] == 'conflict'
    assert response.data['message'] == 'Already exists'


def test_domain_not_found_returns_404():
    response = _call_handler(DomainNotFound("Student not found"))
    assert response.status_code == 404
    assert response.data['error'] == 'not_found'


def test_domain_permission_denied_returns_403():
    response = _call_handler(DomainPermissionDenied("Admin only"))
    assert response.status_code == 403
    assert response.data['error'] == 'permission_denied'


def test_subclass_of_domain_error_uses_its_code():
    """Custom subclass with explicit code is honored."""
    class MyError(DomainError):
        status_code = 422
        error_code = 'my_custom_error'

    response = _call_handler(MyError("Custom"))
    assert response.status_code == 422
    assert response.data['error'] == 'my_custom_error'


def test_drf_default_validation_error_still_works():
    from rest_framework.exceptions import ValidationError as DRFValidationError
    response = _call_handler(DRFValidationError({'field': ['required']}))
    assert response is not None
    assert response.status_code == 400


def test_unhandled_python_exception_returns_500_with_safe_message():
    """Unexpected errors don't leak internals."""
    response = _call_handler(RuntimeError("internal detail"))
    assert response is not None
    assert response.status_code == 500
    assert response.data['error'] == 'internal_error'
    # Should NOT leak the internal error detail
    assert 'internal detail' not in response.data.get('message', '')
