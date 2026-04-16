"""Factory Boy factories for students models."""
import factory
from students.models import Faculty, Department, Programme, Student
from accounts.tests.factories import UserFactory


class FacultyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Faculty

    name = factory.Sequence(lambda n: f'Faculty of Science {n}')
    code = factory.Sequence(lambda n: f'FSC{n:03d}')
    dean = None


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f'Computer Science {n}')
    code = factory.Sequence(lambda n: f'CSC{n:03d}')
    faculty = factory.SubFactory(FacultyFactory)
    hod = None


class ProgrammeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Programme

    name = factory.Sequence(lambda n: f'BSc Computer Science {n}')
    code = factory.Sequence(lambda n: f'BCS{n:03d}')
    department = factory.SubFactory(DepartmentFactory)
    degree_type = 'bachelor'
    duration_years = 4


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(UserFactory, user_type='student')
    programme = factory.SubFactory(ProgrammeFactory)
    level = '100'
    status = 'active'
    matric_number = factory.Sequence(lambda n: f'2024/BCS000/{n:04d}')
    jamb_number = factory.Sequence(lambda n: f'JAMB{n:08d}')
    admission_year = 2024
    expected_graduation_year = 2028
