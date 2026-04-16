"""Tests for academic.services — RegistrationService, ResultService,
SessionService, SemesterService."""
import pytest
from academic.exceptions import AlreadyPublished, CourseNotFound, RegistrationClosed
from academic.models import AcademicSession, CourseRegistration, Result
from academic.services import (
    RegistrationService,
    ResultService,
    SemesterService,
    SessionService,
)
from academic.tests.factories import (
    AcademicSessionFactory,
    CourseAllocationFactory,
    CourseFactory,
    CourseRegistrationFactory,
    ResultFactory,
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


# ---------------------------------------------------------------------------
# ResultService tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCalculateGpaCgpa:
    """Tests for ResultService.calculate_gpa_cgpa."""

    def test_single_result(self):
        """A single result should return the grade_point as GPA."""
        student = StudentFactory()
        semester = SemesterFactory()
        course = CourseFactory(credit_units=3)
        # ca_score=30, exam_score=40 → total=70 → grade A → grade_point 4.0
        ResultFactory(
            student=student, course=course, semester=semester,
            ca_score=30.0, exam_score=40.0,
        )

        data = ResultService.calculate_gpa_cgpa(student, semester=semester)

        assert data['gpa'] == 4.0
        assert data['total_credits'] == 3

    def test_mixed_grades(self):
        """Two results with different grades: weighted average."""
        student = StudentFactory()
        semester = SemesterFactory()
        programme = CourseFactory._meta.model.objects.none()  # unused
        # Course A: 3 credits, grade A (4.0) → ca=30 exam=40 total=70
        course_a = CourseFactory(credit_units=3)
        ResultFactory(
            student=student, course=course_a, semester=semester,
            ca_score=30.0, exam_score=40.0,
        )
        # Course B: 2 credits, grade C (3.0) → ca=20 exam=30 total=50
        course_b = CourseFactory(credit_units=2)
        ResultFactory(
            student=student, course=course_b, semester=semester,
            ca_score=20.0, exam_score=30.0,
        )

        data = ResultService.calculate_gpa_cgpa(student, semester=semester)

        # GPA = (4.0*3 + 3.0*2) / (3+2) = 18/5 = 3.6
        assert data['gpa'] == 3.6
        assert data['total_credits'] == 5

    def test_no_results_returns_zero(self):
        """Student with no results → gpa=0."""
        student = StudentFactory()

        data = ResultService.calculate_gpa_cgpa(student)

        assert data['gpa'] == 0.0
        assert data['total_credits'] == 0


@pytest.mark.django_db
class TestPublishResult:
    """Tests for ResultService.publish_result."""

    def test_publishes_unpublished_result(self):
        """Should set is_published to True."""
        result = ResultFactory(is_published=False)

        updated = ResultService.publish_result(result, by=result.entered_by)

        assert updated.is_published is True
        result.refresh_from_db()
        assert result.is_published is True

    def test_raises_if_already_published(self):
        """Should raise AlreadyPublished for a published result."""
        result = ResultFactory(is_published=True)

        with pytest.raises(AlreadyPublished):
            ResultService.publish_result(result, by=result.entered_by)


# ---------------------------------------------------------------------------
# SessionService tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSessionService:
    """Tests for SessionService."""

    def test_activate_session_deactivates_previous(self):
        """Activating a session should deactivate all others."""
        session1 = AcademicSessionFactory(is_current=True)
        session2 = AcademicSessionFactory(is_current=False)

        activated = SessionService.activate_session(session2, by=None)

        assert activated.is_current is True
        session1.refresh_from_db()
        assert session1.is_current is False

    def test_get_current_returns_active_session(self):
        """get_current should return the session with is_current=True."""
        session = AcademicSessionFactory(is_current=True)

        current = SessionService.get_current()

        assert current is not None
        assert current.id == session.id

    def test_get_current_returns_none_when_no_active(self):
        """get_current returns None when no session is current."""
        AcademicSessionFactory(is_current=False)

        assert SessionService.get_current() is None


# ---------------------------------------------------------------------------
# SemesterService tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSemesterService:
    """Tests for SemesterService."""

    def test_get_active_returns_active_semester(self):
        """Should return the semester with is_active=True."""
        semester = SemesterFactory(is_active=True)

        active = SemesterService.get_active()

        assert active is not None
        assert active.id == semester.id

    def test_get_active_returns_none_when_no_active(self):
        """Returns None when no semester is active."""
        SemesterFactory(is_active=False)

        assert SemesterService.get_active() is None
