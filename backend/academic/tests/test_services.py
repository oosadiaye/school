"""Tests for academic.services — RegistrationService."""
import pytest
from academic.exceptions import CourseNotFound, RegistrationClosed
from academic.models import CourseRegistration
from academic.services import RegistrationService
from academic.tests.factories import (
    AcademicSessionFactory,
    CourseAllocationFactory,
    CourseFactory,
    CourseRegistrationFactory,
    SemesterFactory,
)
from students.tests.factories import StudentFactory


@pytest.mark.django_db
class TestRegisterCoursesBulk:
    """Tests for RegistrationService.register_courses_bulk."""

    def test_creates_registrations(self):
        """Happy path: registers courses for a student."""
        session = AcademicSessionFactory(is_registration_open=True)
        semester = SemesterFactory(session=session)
        student = StudentFactory()
        course1 = CourseFactory()
        course2 = CourseFactory()

        result = RegistrationService.register_courses_bulk(
            student=student,
            course_ids=[course1.id, course2.id],
            semester=semester,
        )

        assert result['registered_count'] == 2
        assert CourseRegistration.objects.filter(student=student).count() == 2

    def test_raises_when_registration_closed(self):
        """Should raise RegistrationClosed when session flag is False."""
        session = AcademicSessionFactory(is_registration_open=False)
        semester = SemesterFactory(session=session)
        student = StudentFactory()
        course = CourseFactory()

        with pytest.raises(RegistrationClosed):
            RegistrationService.register_courses_bulk(
                student=student,
                course_ids=[course.id],
                semester=semester,
            )

    def test_skips_duplicates(self):
        """Already-registered courses should be skipped, not duplicated."""
        session = AcademicSessionFactory(is_registration_open=True)
        semester = SemesterFactory(session=session)
        student = StudentFactory()
        course_existing = CourseFactory()
        course_new = CourseFactory()

        # Pre-register one course
        CourseRegistrationFactory(
            student=student, course=course_existing, semester=semester,
        )

        result = RegistrationService.register_courses_bulk(
            student=student,
            course_ids=[course_existing.id, course_new.id],
            semester=semester,
        )

        # Only the new course should have been created
        assert result['registered_count'] == 1
        assert CourseRegistration.objects.filter(student=student).count() == 2

    def test_raises_when_course_not_found(self):
        """Non-existent course IDs should raise CourseNotFound."""
        session = AcademicSessionFactory(is_registration_open=True)
        semester = SemesterFactory(session=session)
        student = StudentFactory()

        with pytest.raises(CourseNotFound):
            RegistrationService.register_courses_bulk(
                student=student,
                course_ids=[99999],
                semester=semester,
            )

    def test_all_duplicates_returns_zero_registered(self):
        """When all requested courses are already registered, count is 0."""
        session = AcademicSessionFactory(is_registration_open=True)
        semester = SemesterFactory(session=session)
        student = StudentFactory()
        course = CourseFactory()

        CourseRegistrationFactory(
            student=student, course=course, semester=semester,
        )

        result = RegistrationService.register_courses_bulk(
            student=student,
            course_ids=[course.id],
            semester=semester,
        )

        assert result['registered_count'] == 0
        assert CourseRegistration.objects.filter(student=student).count() == 1


@pytest.mark.django_db
class TestGetStudentCourses:
    """Tests for RegistrationService.get_student_courses."""

    def test_returns_registered_courses(self):
        """Should return the student's registrations."""
        session = AcademicSessionFactory(is_registration_open=True)
        semester = SemesterFactory(session=session)
        student = StudentFactory()
        course = CourseFactory()
        CourseRegistrationFactory(
            student=student, course=course, semester=semester,
        )

        qs = RegistrationService.get_student_courses(student)
        assert qs.count() == 1
        assert qs.first().course_id == course.id

    def test_filters_by_semester(self):
        """When semester is passed, only that semester's registrations return."""
        session = AcademicSessionFactory(is_registration_open=True)
        sem1 = SemesterFactory(session=session, name='first')
        sem2 = SemesterFactory(session=session, name='second')
        student = StudentFactory()

        CourseRegistrationFactory(student=student, semester=sem1)
        CourseRegistrationFactory(student=student, semester=sem2)

        qs = RegistrationService.get_student_courses(student, semester=sem1)
        assert qs.count() == 1
        assert qs.first().semester_id == sem1.id

    def test_returns_empty_for_no_registrations(self):
        """Student with no registrations should get an empty queryset."""
        student = StudentFactory()
        qs = RegistrationService.get_student_courses(student)
        assert qs.count() == 0
