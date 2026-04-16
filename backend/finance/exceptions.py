"""Domain exceptions for the finance app."""
from core.exceptions import ConflictError, DomainError, NotFound, ValidationFailed


class InvoiceExists(ConflictError):
    """Invoice already exists for this student and fee structure."""

    error_code = 'invoice_exists'


class NoFeeStructureFound(NotFound):
    """No matching fee structure found for the given criteria."""

    error_code = 'no_fee_structure_found'


class InvalidPaymentProvider(ValidationFailed):
    """Payment provider is not supported."""

    error_code = 'invalid_payment_provider'


class PaymentInitiationFailed(DomainError):
    """Upstream payment gateway failed to initiate a transaction."""

    status_code = 502
    error_code = 'payment_initiation_failed'


class PaymentVerificationFailed(DomainError):
    """Upstream payment gateway failed to verify a transaction."""

    status_code = 502
    error_code = 'payment_verification_failed'


class PaymentAlreadyVerified(ConflictError):
    """Payment has already been verified and processed."""

    error_code = 'payment_already_verified'


class WaiverAlreadyApproved(ConflictError):
    """Fee waiver has already been approved."""

    error_code = 'waiver_already_approved'
