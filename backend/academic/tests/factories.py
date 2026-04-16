"""Factory Boy factories for academic models."""
import datetime

import factory
from academic.models import (
    AcademicSession,
    Attendance,
    Semester,
    Course,
    CourseAllocation,
    CourseRegistration,
    ExamSitting,
    Result,
)
from accounts.tests.factories import UserFactory
from students.tests.factories import ProgrammeFactory, StudentFactory


class AcademicSessionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AcademicSession

    name = factory.Sequence(lambda n: f'2024/{2025 + n}')
    start_date = factory.LazyFunction(lambda: datetime.date(2024, 9, 1))
    end_date = factory.LazyFunction(lambda: datetime.date(2025, 7, 31))
    is_current = True
    is_registration_open = True
    is_exam_enabled = False


class SemesterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Semester

    name = 'first'
    session = factory.SubFactory(AcademicSessionFactory)
    start_date = factory.LazyFunction(lambda: datetime.date(2024, 9, 1))
    end_date = factory.LazyFunction(lambda: datetime.date(2025, 1, 31))
    is_active = True


class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Course

    programme = factory.SubFactory(ProgrammeFactory)
    code = factory.Sequence(lambda n: f'CSC{n + 101}')
    name = factory.Sequence(lambda n: f'Introduction to Computing {n}')
    credit_units = 3
    level = '100'
    semester = 'first'


class CourseAllocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseAllocation

    course = factory.SubFactory(CourseFactory)
    lecturer = factory.SubFactory(UserFactory, user_type='lecturer')
    semester = factory.SubFactory(SemesterFactory)


class CourseRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CourseRegistration

    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    semester = factory.SubFactory(SemesterFactory)
    status = 'registered'


class ResultFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Result

    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    semester = factory.SubFactory(SemesterFactory)
    ca_score = 30.0
    exam_score = 50.0
    entered_by = factory.SubFactory(UserFactory, user_type='lecturer')
    is_published = False


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    semester = factory.SubFactory(SemesterFactory)
    total_classes = 10
    attended_classes = 8


class ExamSittingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExamSitting

    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)
    semester = factory.SubFactory(SemesterFactory)
    venue = 'Main Hall'
    seat_number = factory.Sequence(lambda n: f'{n + 1:03d}')
    date = factory.LazyFunction(lambda: datetime.date(2025, 6, 15))
    time = factory.LazyFunction(lambda: datetime.time(9, 0))
