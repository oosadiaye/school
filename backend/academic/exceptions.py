"""Domain exceptions for the academic app."""
from core.exceptions import DomainError, ConflictError, NotFound


class RegistrationClosed(ConflictError):
    """Course registration is not open for the current session."""

    error_code = 'registration_closed'


class CourseNotFound(NotFound):
    """One or more requested courses do not exist."""

    error_code = 'course_not_found'


class CreditOverload(DomainError):
    """Student would exceed the maximum allowed credit units."""

    status_code = 422
    error_code = 'credit_overload'


class AlreadyPublished(ConflictError):
    """Result has already been published and cannot be modified."""

    error_code = 'already_published'
