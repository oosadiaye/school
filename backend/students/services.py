"""Business logic for students: profiles, status transitions, cascade validation."""
from __future__ import annotations

from django.db.models import QuerySet

from core.exceptions import NotFound
from students.exceptions import InvalidStatusTransition, HasActiveRecords
from students.models import Student, Faculty, Department, Programme


class StudentService:
    """Handles student profile lookup, status transitions, and queryset scoping."""

    VALID_TRANSITIONS: dict[str, list[str]] = {
        'active': ['suspended', 'withdrawn', 'graduated', 'deferred'],
        'suspended': ['active', 'expelled'],
        'deferred': ['active', 'withdrawn'],
        'withdrawn': [],
        'graduated': [],
    }

    @staticmethod
    def get_profile_for_user(user) -> Student:
        """Return the Student record linked to *user*.

        Raises:
            NotFound: no student profile exists for this user.
        """
        try:
            return Student.objects.select_related(
                'user', 'programme__department__faculty',
            ).get(user=user)
        except Student.DoesNotExist:
            raise NotFound('Student profile not found.')

    @classmethod
    def update_status(cls, student: Student, new_status: str, *, by=None) -> Student:
        """Transition *student* to *new_status* if the transition is valid.

        Raises:
            InvalidStatusTransition: transition not in the allowed map.
        """
        current = student.status
        allowed = cls.VALID_TRANSITIONS.get(current, [])

        if new_status not in allowed:
            raise InvalidStatusTransition(
                f'Cannot transition from {current!r} to {new_status!r}.',
                details={
                    'current_status': current,
                    'requested_status': new_status,
                    'allowed_transitions': allowed,
                },
            )

        student.status = new_status
        student.save(update_fields=['status'])
        return student

    @staticmethod
    def filter_for_user(user) -> QuerySet[Student]:
        """Return the queryset a given user is allowed to see.

        - student: own record only
        - admin / staff: all students
        - parent: empty (placeholder for future)
        """
        base = Student.objects.select_related(
            'user', 'programme__department__faculty',
        )

        if user.user_type == 'student':
            return base.filter(user=user)
        if user.user_type in ('admin', 'staff'):
            return base.all()
        # parent or unknown
        return base.none()


class FacultyService:
    """Cascade-safe operations on Faculty."""

    @staticmethod
    def safe_delete(faculty: Faculty, *, by=None) -> None:
        """Delete *faculty* only if it has no departments.

        Raises:
            HasActiveRecords: faculty still owns departments.
        """
        if faculty.departments.exists():
            raise HasActiveRecords('Faculty has active departments.')
        faculty.delete()


class DepartmentService:
    """Cascade-safe operations on Department."""

    @staticmethod
    def safe_delete(department: Department, *, by=None) -> None:
        """Delete *department* only if it has no programmes.

        Raises:
            HasActiveRecords: department still owns programmes.
        """
        if department.programmes.exists():
            raise HasActiveRecords('Department has active programmes.')
        department.delete()


class ProgrammeService:
    """Cascade-safe operations on Programme."""

    @staticmethod
    def safe_delete(programme: Programme, *, by=None) -> None:
        """Delete *programme* only if it has no students.

        Raises:
            HasActiveRecords: programme still has enrolled students.
        """
        if programme.students.exists():
            raise HasActiveRecords('Programme has active students.')
        programme.delete()
