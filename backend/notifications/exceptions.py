"""Custom exceptions for the notifications app."""
from core.exceptions import DomainError, NotFound, PermissionDenied


class NotificationNotFound(NotFound):
    """Raised when a notification does not exist."""
    error_code = 'notification_not_found'


class NotificationPermissionDenied(PermissionDenied):
    """Raised when a user tries to act on another user's notification."""
    error_code = 'notification_permission_denied'


class TemplateNotFound(NotFound):
    """Raised when an email or SMS template does not exist."""
    error_code = 'template_not_found'
