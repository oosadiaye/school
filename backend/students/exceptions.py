"""Domain exceptions for students app."""
from core.exceptions import DomainError, ConflictError


class InvalidStatusTransition(DomainError):
    """Raised when a student status change violates allowed transitions."""

    status_code = 409
    error_code = 'invalid_status_transition'


class HasActiveRecords(ConflictError):
    """Raised when deleting an entity that still has active children."""

    error_code = 'has_active_records'
