"""Business logic for the academic app."""
from __future__ import annotations

from typing import List, Optional

from django.db import transaction
from django.db.models import Count, F, QuerySet, Sum

from academic.exceptions import AlreadyPublished, CourseNotFound, RegistrationClosed
from academic.models import (
    AcademicSession,
    Course,
    CourseRegistration,
    Result,
    Semester,
)


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


class ResultService:
    """Handles result queries, GPA calculation, and publishing."""

    @staticmethod
    def calculate_gpa_cgpa(student, semester=None) -> dict:
        """Calculate GPA (and optionally CGPA) for a student.

        Replicates the aggregation logic from the former ``calculate_gpa`` view:
        GPA = Sum(grade_point * credit_units) / Sum(credit_units)
        """
        results = Result.objects.filter(
            student=student,
            grade_point__isnull=False,
            course__credit_units__isnull=False,
        )

        if semester is not None:
            results = results.filter(semester=semester)

        if not results.exists():
            return {'gpa': 0.0, 'total_credits': 0, 'results_count': 0}

        aggregated = results.annotate(
            weighted_points=F('grade_point') * F('course__credit_units'),
        ).aggregate(
            total_points=Sum('weighted_points'),
            total_units=Sum('course__credit_units'),
            results_count=Count('id'),
        )

        total_points = aggregated['total_points'] or 0
        total_units = aggregated['total_units'] or 0
        gpa = total_points / total_units if total_units > 0 else 0

        return {
            'gpa': round(gpa, 2),
            'total_credits': total_units,
            'results_count': aggregated['results_count'],
        }

    @staticmethod
    def publish_result(result: Result, by) -> Result:
        """Publish a result. Raises AlreadyPublished if already published."""
        if result.is_published:
            raise AlreadyPublished('Result has already been published.')

        result.is_published = True
        result.save(update_fields=['is_published', 'updated_at'])
        return result

    @staticmethod
    def get_student_results(student, semester=None) -> QuerySet[Result]:
        """Return a student's results, optionally filtered by semester."""
        qs = Result.objects.select_related(
            'student__user', 'course', 'semester', 'entered_by',
        ).filter(student=student)

        if semester is not None:
            qs = qs.filter(semester=semester)

        return qs


class SessionService:
    """Handles academic session activation and lookup."""

    @staticmethod
    def activate_session(session: AcademicSession, by) -> AcademicSession:
        """Activate a session, deactivating all others atomically."""
        with transaction.atomic():
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
            session.is_current = True
            session.save(update_fields=['is_current', 'updated_at'])
        return session

    @staticmethod
    def get_current() -> AcademicSession | None:
        """Return the currently active academic session, or None."""
        return AcademicSession.objects.filter(is_current=True).first()


class SemesterService:
    """Handles semester lookup."""

    @staticmethod
    def get_active() -> Semester | None:
        """Return the currently active semester, or None."""
        return Semester.objects.filter(is_active=True).first()
