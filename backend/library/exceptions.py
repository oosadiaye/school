"""Domain exceptions for the library app."""
from core.exceptions import ConflictError, DomainError, ValidationFailed


class BookUnavailable(ValidationFailed):
    """No available copies of the requested book."""

    error_code = 'book_unavailable'


class LoanNotActive(ValidationFailed):
    """Loan is not in an active/borrowed state."""

    error_code = 'loan_not_active'


class AlreadyReserved(ConflictError):
    """Member already has an active reservation for this book."""

    error_code = 'already_reserved'
