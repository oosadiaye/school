"""Business logic for the academic app — course registration."""
from __future__ import annotations

from typing import List, Optional

from django.db import transaction
from django.db.models import QuerySet

from academic.exceptions import CourseNotFound, RegistrationClosed
from academic.models import Course, CourseRegistration


class RegistrationService:
    """Handles course registration and retrieval for students."""

    @staticmethod
    def register_courses_bulk(
        student,
        course_ids: List[int],
        semester,
    ) -> dict:
        """Register a student for multiple courses in a single semester.

        Replicates the logic previously in CourseRegistrationViewSet.register_courses.

        1. Verify the session's is_registration_open flag.
        2. Validate that every course_id exists.
        3. De-duplicate against existing registrations.
        4. Bulk-create new CourseRegistration records atomically.

        Returns:
            dict with 'registered_count' and 'message'.

        Raises:
            RegistrationClosed: session registration is not open.
            CourseNotFound: one or more course IDs do not exist.
        """
        # 1. Check registration is open via the semester's session
        if not semester.session.is_registration_open:
            raise RegistrationClosed(
                'Course registration is closed for this session.'
            )

        # 2. Validate all course IDs exist
        existing_courses = set(
            Course.objects.filter(id__in=course_ids).values_list('id', flat=True)
        )
        missing = set(course_ids) - existing_courses
        if missing:
            raise CourseNotFound(
                f'Courses not found: {sorted(missing)}',
                details={'missing_ids': sorted(missing)},
            )

        # 3. Find already-registered courses for this student + semester
        already_registered = set(
            CourseRegistration.objects.filter(
                student=student,
                semester=semester,
                course_id__in=course_ids,
            ).values_list('course_id', flat=True)
        )

        # 4. Build and bulk-create new registrations
        new_course_ids = [
            cid for cid in course_ids if cid not in already_registered
        ]

        new_registrations = [
            CourseRegistration(
                student=student,
                course_id=course_id,
                semester=semester,
                status='registered',
            )
            for course_id in new_course_ids
        ]

        with transaction.atomic():
            CourseRegistration.objects.bulk_create(
                new_registrations, ignore_conflicts=True,
            )

        registered_count = len(new_registrations)
        return {
            'registered_count': registered_count,
            'message': f'{registered_count} courses registered successfully',
        }

    @staticmethod
    def get_student_courses(
        student,
        semester=None,
    ) -> QuerySet[CourseRegistration]:
        """Return a student's course registrations, optionally filtered by semester.

        Uses select_related for performance.
        """
        qs = CourseRegistration.objects.select_related(
            'student__user', 'course', 'semester', 'course__programme',
        ).filter(student=student)

        if semester is not None:
            qs = qs.filter(semester=semester)

        return qs
