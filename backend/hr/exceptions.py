"""Custom exceptions for the HR app."""


class InsufficientLeaveBalance(Exception):
    """Raised when an employee does not have enough leave days."""

    def __init__(self, available: int, requested: int) -> None:
        self.available = available
        self.requested = requested
        super().__init__(
            f"Insufficient leave balance: {available} day(s) available, "
            f"{requested} day(s) requested."
        )


class AlreadyCheckedIn(Exception):
    """Raised when an employee already has an open attendance record today."""

    def __init__(self, employee_id: str) -> None:
        self.employee_id = employee_id
        super().__init__(
            f"Employee {employee_id} has already checked in today."
        )


class NotCheckedIn(Exception):
    """Raised when an employee has no open attendance record to check out of."""

    def __init__(self, employee_id: str) -> None:
        self.employee_id = employee_id
        super().__init__(
            f"Employee {employee_id} has not checked in today."
        )
