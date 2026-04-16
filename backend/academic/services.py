"""Business logic for the academic app."""
from __future__ import annotations

from typing import List, Optional

from django.db import transaction
from django.db.models import Count, F, QuerySet, Sum

from core.exceptions import ConflictError
from academic.exceptions import AlreadyPublished, CourseNotFound, RegistrationClosed
from academic.models import (
    AcademicSession,
    Attendance,
    Course,
    CourseAllocation,
    CourseRegistration,
    ExamSitting,
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


class CourseService:
    """Handles course lifecycle operations."""

    @staticmethod
    def safe_delete(course: Course, by) -> None:
        """Delete a course only if it has no active registrations.

        Raises:
            ConflictError: if the course has any CourseRegistration records.
        """
        if CourseRegistration.objects.filter(course=course).exists():
            raise ConflictError('Course has active registrations')
        course.delete()

    @staticmethod
    def allocate_to_lecturer(
        course: Course,
        lecturer,
        session,
        by,
    ) -> CourseAllocation:
        """Create a course allocation for a lecturer in a given session."""
        semester = Semester.objects.filter(session=session, is_active=True).first()
        allocation, _created = CourseAllocation.objects.get_or_create(
            course=course,
            semester=semester,
            defaults={'lecturer': lecturer},
        )
        return allocation


class AttendanceService:
    """Handles attendance marking and summaries."""

    @staticmethod
    def mark_attendance(
        student,
        course: Course,
        semester: Semester,
        total_classes: int,
        attended_classes: int,
    ) -> Attendance:
        """Create or update an attendance record for the student+course+semester.

        Uses update_or_create to avoid duplicates.
        """
        attendance, _created = Attendance.objects.update_or_create(
            student=student,
            course=course,
            semester=semester,
            defaults={
                'total_classes': total_classes,
                'attended_classes': attended_classes,
            },
        )
        return attendance

    @staticmethod
    def get_course_summary(course: Course, semester: Semester) -> dict:
        """Return per-student attendance percentages for a course+semester."""
        records = Attendance.objects.filter(
            course=course, semester=semester,
        ).select_related('student__user')

        return {
            record.student.matric_number: record.attendance_percentage
            for record in records
        }


class ExamSittingService:
    """Handles exam seating generation."""

    @staticmethod
    def generate_seating_for_course(
        course: Course,
        semester: Semester,
        venue: str = 'Main Hall',
        exam_date=None,
        exam_time: str = '09:00',
        seat_prefix: str = '',
    ) -> List[ExamSitting]:
        """Generate sequential exam sittings for all registered students.

        Replicates the logic from the former generate_seating view action:
        1. Get all registered student IDs for the course+semester.
        2. Exclude students who already have an ExamSitting.
        3. Assign sequential seat numbers (f"{idx+1:03d}").
        4. Bulk-create and return the new sittings.
        """
        registered_student_ids = list(
            CourseRegistration.objects.filter(
                course=course,
                semester=semester,
                status='registered',
            ).select_related('student').values_list('student_id', flat=True)
        )

        existing_seated = set(
            ExamSitting.objects.filter(
                course=course,
                semester=semester,
            ).values_list('student_id', flat=True)
        )

        new_sittings = [
            ExamSitting(
                student_id=student_id,
                course=course,
                semester=semester,
                venue=venue,
                seat_number=f'{idx + 1:03d}',
                date=exam_date,
                time=exam_time,
            )
            for idx, student_id in enumerate(
                sid for sid in registered_student_ids
                if sid not in existing_seated
            )
        ]

        ExamSitting.objects.bulk_create(new_sittings, ignore_conflicts=True)
        return new_sittings
