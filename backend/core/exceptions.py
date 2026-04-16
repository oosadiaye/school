"""Domain exception hierarchy and custom DRF exception handler.

All service-layer business-rule violations should raise a subclass of
DomainError. The custom handler translates them into standardized JSON
responses with the right HTTP status.

Response format:
    {"error": "<error_code>", "message": "<human readable>", "details": {...}}
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler


logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base exception for all business-rule violations raised by services.

    Subclasses should override status_code and error_code.
    Use details={} to pass structured context (field errors, offending IDs, etc.).
    """

    status_code: int = 400
    error_code: str = 'domain_error'

    def __init__(self, message: str = '', details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message or self.__class__.__name__
        self.details = details or {}


class ValidationFailed(DomainError):
    """Input validation failed (distinct from DRF serializer ValidationError)."""

    status_code = 400
    error_code = 'validation_failed'


class PermissionDenied(DomainError):
    """User is authenticated but not authorized for this action."""

    status_code = 403
    error_code = 'permission_denied'


class NotFound(DomainError):
    """Requested resource does not exist."""

    status_code = 404
    error_code = 'not_found'


class ConflictError(DomainError):
    """State conflict — e.g., invoice already exists, registration closed."""

    status_code = 409
    error_code = 'conflict'


def _build_error_payload(
    error_code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Compose the standardized error response body."""
    payload: Dict[str, Any] = {
        'error': error_code,
        'message': message,
        'details': details or {},
    }
    return payload


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """DRF exception handler with domain-error and safe-default support.

    1. If `exc` is a DomainError, translate using its status_code/error_code.
    2. Else delegate to DRF's default handler (for ValidationError, NotFound, etc).
    3. If DRF's handler returns None (unhandled Python exception), return a
       generic 500 with a safe message — do not leak internals.
    """
    if isinstance(exc, DomainError):
        return Response(
            _build_error_payload(exc.error_code, exc.message, exc.details),
            status=exc.status_code,
        )

    response = drf_default_handler(exc, context)
    if response is not None:
        # Normalize DRF's response into our shape so clients see one format.
        data = response.data
        if isinstance(data, dict) and 'detail' in data and len(data) == 1:
            # Most DRF exceptions use {"detail": "..."}
            response.data = _build_error_payload(
                error_code=_drf_status_to_code(response.status_code),
                message=str(data['detail']),
            )
        else:
            # Serializer validation returns field-keyed dicts — preserve as details
            response.data = _build_error_payload(
                error_code='validation_failed',
                message='Validation error',
                details=data if isinstance(data, dict) else {'errors': data},
            )
        return response

    # Unhandled Python exception — log with traceback, return safe 500.
    logger.exception('Unhandled exception in %s: %s', context.get('view'), exc)
    return Response(
        _build_error_payload(
            error_code='internal_error',
            message='An unexpected error occurred. Please try again later.',
        ),
        status=500,
    )


def _drf_status_to_code(status_code: int) -> str:
    """Map HTTP status to our error_code vocabulary."""
    return {
        400: 'bad_request',
        401: 'unauthenticated',
        403: 'permission_denied',
        404: 'not_found',
        405: 'method_not_allowed',
        409: 'conflict',
        415: 'unsupported_media_type',
        429: 'throttled',
    }.get(status_code, 'error')
