"""Custom exceptions for the hostel app."""


class GenderMismatch(Exception):
    """Raised when student gender does not match hostel type."""

    def __init__(self, hostel_type: str, student_gender: str) -> None:
        self.hostel_type = hostel_type
        self.student_gender = student_gender
        super().__init__(
            f"Hostel is '{hostel_type}' only but student gender is '{student_gender}'."
        )


class RoomFull(Exception):
    """Raised when a room has reached its capacity."""

    def __init__(self, room_number: str, capacity: int) -> None:
        self.room_number = room_number
        self.capacity = capacity
        super().__init__(
            f"Room {room_number} is full (capacity: {capacity})."
        )


class AlreadyAllocated(Exception):
    """Raised when a student already has an active hostel assignment for the session."""

    def __init__(self, matric_number: str, session: str) -> None:
        self.matric_number = matric_number
        self.session = session
        super().__init__(
            f"Student {matric_number} already has an active assignment for {session}."
        )
