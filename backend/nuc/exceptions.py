"""Custom exceptions for the NUC app."""
from core.exceptions import DomainError, NotFound


class AccreditationNotFound(NotFound):
    """Raised when an accreditation record does not exist."""
    error_code = 'accreditation_not_found'


class ChecklistNotFound(NotFound):
    """Raised when a compliance checklist does not exist."""
    error_code = 'checklist_not_found'


class ReportNotFound(NotFound):
    """Raised when a NUC report does not exist."""
    error_code = 'report_not_found'
