"""Tests for serializer-level validation across all apps (Phase 2 Task 16)."""
import datetime
from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from accounts.serializers import UserSerializer, UserCreateSerializer
from academic.serializers import ResultCreateSerializer, CourseRegistrationSerializer
from finance.serializers import InvoiceSerializer, PaymentSerializer, FeeWaiverSerializer
from hr.serializers import LeaveRequestSerializer
from hostel.serializers import HostelAssignmentSerializer
from library.serializers import BookLoanSerializer

from accounts.tests.factories import UserFactory
from academic.tests.factories import (
    CourseFactory, SemesterFactory, ResultFactory, CourseRegistrationFactory,
)
from finance.tests.factories import (
    InvoiceFactory, PaymentFactory, FeeWaiverFactory, FeeStructureFactory,
)
from hr.tests.factories import LeaveRequestFactory, EmployeeFactory, LeaveTypeFactory
from hostel.tests.factories import HostelFactory, RoomFactory, HostelAssignmentFactory
from library.tests.factories import BookLoanFactory, BookFactory, LibraryMemberFactory
from students.tests.factories import StudentFactory


pytestmark = pytest.mark.django_db


# ── accounts: phone validation ──────────────────────────────────────────

class TestUserPhoneValidation:
    def test_valid_phone_accepted(self):
        user = UserFactory()
        s = UserSerializer(user, data={'phone': '+2348012345678'}, partial=True)
        assert s.is_valid(), s.errors

    def test_invalid_phone_format_rejected(self):
        user = UserFactory()
        s = UserSerializer(user, data={'phone': 'not-a-phone'}, partial=True)
        assert not s.is_valid()
        assert 'phone' in s.errors

    def test_blank_phone_accepted(self):
        user = UserFactory()
        s = UserSerializer(user, data={'phone': ''}, partial=True)
        assert s.is_valid(), s.errors

    def test_create_serializer_invalid_phone_rejected(self):
        data = {
            'username': 'newuser',
            'email': 'new@test.local',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'student',
            'phone': 'abc123',
        }
        s = UserCreateSerializer(data=data)
        assert not s.is_valid()
        assert 'phone' in s.errors


# ── academic: result score validation ────────────────────────────────────

class TestResultScoreValidation:
    def test_ca_score_over_40_rejected(self):
        student = StudentFactory()
        course = CourseFactory()
        semester = SemesterFactory()
        lecturer = UserFactory(user_type='lecturer')
        data = {
            'student': student.pk,
            'course': course.pk,
            'semester': semester.pk,
            'ca_score': 45,
            'exam_score': 50,
        }
        s = ResultCreateSerializer(data=data)
        assert not s.is_valid()

    def test_exam_score_over_60_rejected(self):
        student = StudentFactory()
        course = CourseFactory()
        semester = SemesterFactory()
        data = {
            'student': student.pk,
            'course': course.pk,
            'semester': semester.pk,
            'ca_score': 30,
            'exam_score': 65,
        }
        s = ResultCreateSerializer(data=data)
        assert not s.is_valid()

    def test_ca_exam_sum_over_100_rejected(self):
        student = StudentFactory()
        course = CourseFactory()
        semester = SemesterFactory()
        data = {
            'student': student.pk,
            'course': course.pk,
            'semester': semester.pk,
            'ca_score': 40,
            'exam_score': 60.5,
        }
        s = ResultCreateSerializer(data=data)
        assert not s.is_valid()

    def test_valid_scores_accepted(self):
        student = StudentFactory()
        course = CourseFactory()
        semester = SemesterFactory()
        data = {
            'student': student.pk,
            'course': course.pk,
            'semester': semester.pk,
            'ca_score': 30,
            'exam_score': 50,
        }
        s = ResultCreateSerializer(data=data)
        assert s.is_valid(), s.errors


# ── academic: course registration semester validation ────────────────────

class TestCourseRegistrationSemesterValidation:
    def test_inactive_semester_rejected(self):
        semester = SemesterFactory(is_active=False)
        student = StudentFactory()
        course = CourseFactory()
        data = {
            'student': student.pk,
            'course': course.pk,
            'semester': semester.pk,
        }
        s = CourseRegistrationSerializer(data=data)
        assert not s.is_valid()
        assert 'semester' in s.errors


# ── finance: invoice amount validation ───────────────────────────────────

class TestInvoiceAmountValidation:
    def test_invoice_amount_zero_rejected(self):
        invoice = InvoiceFactory()
        s = InvoiceSerializer(invoice, data={'amount': Decimal('0')}, partial=True)
        assert not s.is_valid()
        assert 'amount' in s.errors

    def test_invoice_negative_amount_rejected(self):
        invoice = InvoiceFactory()
        s = InvoiceSerializer(invoice, data={'amount': Decimal('-100')}, partial=True)
        assert not s.is_valid()
        assert 'amount' in s.errors


# ── finance: payment amount validation ───────────────────────────────────

class TestPaymentAmountValidation:
    def test_payment_amount_zero_rejected(self):
        payment = PaymentFactory()
        s = PaymentSerializer(payment, data={'amount': Decimal('0')}, partial=True)
        assert not s.is_valid()
        assert 'amount' in s.errors


# ── finance: fee waiver validation ───────────────────────────────────────

class TestFeeWaiverValidation:
    def test_fee_waiver_both_amount_and_percentage_rejected(self):
        waiver = FeeWaiverFactory()
        s = FeeWaiverSerializer(waiver, data={
            'student': waiver.student.pk,
            'invoice': waiver.invoice.pk,
            'waiver_type': 'partial',
            'amount': Decimal('5000'),
            'percentage': Decimal('50'),
            'reason': 'Test',
        })
        assert not s.is_valid()

    def test_fee_waiver_percentage_over_100_rejected(self):
        waiver = FeeWaiverFactory()
        s = FeeWaiverSerializer(waiver, data={
            'student': waiver.student.pk,
            'invoice': waiver.invoice.pk,
            'waiver_type': 'partial',
            'amount': Decimal('0'),
            'percentage': Decimal('150'),
            'reason': 'Test',
        })
        assert not s.is_valid()


# ── hr: leave request date validation ────────────────────────────────────

class TestLeaveRequestDateValidation:
    def test_leave_end_before_start_rejected(self):
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory()
        data = {
            'employee': employee.pk,
            'leave_type': leave_type.pk,
            'start_date': '2025-06-10',
            'end_date': '2025-06-05',
            'days': 5,
            'reason': 'Vacation',
        }
        s = LeaveRequestSerializer(data=data)
        assert not s.is_valid()
        assert 'end_date' in s.errors

    def test_leave_end_equals_start_rejected(self):
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory()
        data = {
            'employee': employee.pk,
            'leave_type': leave_type.pk,
            'start_date': '2025-06-10',
            'end_date': '2025-06-10',
            'days': 1,
            'reason': 'Vacation',
        }
        s = LeaveRequestSerializer(data=data)
        assert not s.is_valid()
        assert 'end_date' in s.errors


# ── hostel: gender match validation ──────────────────────────────────────

class TestHostelGenderValidation:
    def test_male_student_in_female_hostel_rejected(self):
        student = StudentFactory()
        student.gender = 'male'
        student.save()
        hostel = HostelFactory(hostel_type='female')
        room = RoomFactory(hostel=hostel)
        data = {
            'student': student.pk,
            'room': room.pk,
            'session': '2024/2025',
        }
        s = HostelAssignmentSerializer(data=data)
        assert not s.is_valid()
        assert 'room' in s.errors

    def test_mixed_hostel_accepts_any_gender(self):
        student = StudentFactory()
        student.gender = 'male'
        student.save()
        hostel = HostelFactory(hostel_type='mixed')
        room = RoomFactory(hostel=hostel)
        data = {
            'student': student.pk,
            'room': room.pk,
            'session': '2024/2025',
        }
        s = HostelAssignmentSerializer(data=data)
        assert s.is_valid(), s.errors


# ── library: book loan due date validation ───────────────────────────────

class TestBookLoanDueDateValidation:
    def test_book_loan_past_due_date_rejected(self):
        book = BookFactory()
        member = LibraryMemberFactory()
        data = {
            'book': book.pk,
            'member': member.pk,
            'due_date': '2020-01-01',
        }
        s = BookLoanSerializer(data=data)
        assert not s.is_valid()
        assert 'due_date' in s.errors

    def test_book_loan_future_due_date_accepted(self):
        book = BookFactory()
        member = LibraryMemberFactory()
        future = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()
        data = {
            'book': book.pk,
            'member': member.pk,
            'due_date': future,
        }
        s = BookLoanSerializer(data=data)
        assert s.is_valid(), s.errors
