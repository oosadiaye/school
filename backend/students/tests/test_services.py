"""Tests for students service layer."""
import pytest
from core.exceptions import NotFound
from students.services import (
    StudentService,
    FacultyService,
    DepartmentService,
    ProgrammeService,
)
from students.exceptions import InvalidStatusTransition, HasActiveRecords
from students.tests.factories import (
    StudentFactory,
    FacultyFactory,
    DepartmentFactory,
    ProgrammeFactory,
)
from accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestStudentServiceGetProfile:
    def test_returns_student_for_valid_user(self):
        student = StudentFactory()
        result = StudentService.get_profile_for_user(student.user)
        assert result.pk == student.pk

    def test_raises_not_found_for_non_student(self):
        admin = UserFactory(user_type='admin')
        with pytest.raises(NotFound):
            StudentService.get_profile_for_user(admin)


@pytest.mark.django_db
class TestStudentServiceUpdateStatus:
    def test_valid_transition_active_to_suspended(self):
        student = StudentFactory(status='active')
        updated = StudentService.update_status(student, 'suspended', by=None)
        assert updated.status == 'suspended'

    def test_invalid_transition_graduated_to_active(self):
        student = StudentFactory(status='graduated')
        with pytest.raises(InvalidStatusTransition):
            StudentService.update_status(student, 'active', by=None)

    def test_valid_transition_active_to_graduated(self):
        student = StudentFactory(status='active')
        updated = StudentService.update_status(student, 'graduated', by=None)
        assert updated.status == 'graduated'

    def test_valid_transition_suspended_to_active(self):
        student = StudentFactory(status='suspended')
        updated = StudentService.update_status(student, 'active', by=None)
        assert updated.status == 'active'


@pytest.mark.django_db
class TestStudentServiceFilter:
    def test_student_sees_only_own_record(self):
        student = StudentFactory()
        StudentFactory()  # another student
        qs = StudentService.filter_for_user(student.user)
        assert qs.count() == 1
        assert qs.first().pk == student.pk

    def test_admin_sees_all_records(self):
        StudentFactory()
        StudentFactory()
        admin = UserFactory(user_type='admin')
        qs = StudentService.filter_for_user(admin)
        assert qs.count() == 2

    def test_staff_sees_all_records(self):
        StudentFactory()
        staff = UserFactory(user_type='staff')
        qs = StudentService.filter_for_user(staff)
        assert qs.count() == 1


@pytest.mark.django_db
class TestFacultyServiceSafeDelete:
    def test_delete_blocked_when_has_departments(self):
        dept = DepartmentFactory()
        with pytest.raises(HasActiveRecords):
            FacultyService.safe_delete(dept.faculty, by=None)

    def test_delete_succeeds_when_empty(self):
        faculty = FacultyFactory()
        FacultyService.safe_delete(faculty, by=None)
        from students.models import Faculty
        assert not Faculty.objects.filter(pk=faculty.pk).exists()


@pytest.mark.django_db
class TestDepartmentServiceSafeDelete:
    def test_delete_blocked_when_has_programmes(self):
        programme = ProgrammeFactory()
        with pytest.raises(HasActiveRecords):
            DepartmentService.safe_delete(programme.department, by=None)

    def test_delete_succeeds_when_empty(self):
        dept = DepartmentFactory()
        DepartmentService.safe_delete(dept, by=None)
        from students.models import Department
        assert not Department.objects.filter(pk=dept.pk).exists()


@pytest.mark.django_db
class TestProgrammeServiceSafeDelete:
    def test_delete_blocked_when_has_students(self):
        student = StudentFactory()
        with pytest.raises(HasActiveRecords):
            ProgrammeService.safe_delete(student.programme, by=None)

    def test_delete_succeeds_when_empty(self):
        programme = ProgrammeFactory()
        ProgrammeService.safe_delete(programme, by=None)
        from students.models import Programme
        assert not Programme.objects.filter(pk=programme.pk).exists()
