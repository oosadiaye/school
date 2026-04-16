"""Factory Boy factories for HR models."""
from datetime import date, timedelta
from decimal import Decimal

import factory
from accounts.tests.factories import UserFactory
from hr.models import Attendance, Department, Employee, LeaveRequest, LeaveType, Payroll


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")
    code = factory.Sequence(lambda n: f"DEP{n:03d}")
    head = factory.SubFactory(UserFactory, user_type="admin")
    description = "A department."


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Employee

    user = factory.SubFactory(UserFactory, user_type="staff")
    employee_id = factory.Sequence(lambda n: f"EMP{n:05d}")
    department = factory.SubFactory(DepartmentFactory)
    designation = "lecturer"
    employment_type = "permanent"
    hire_date = factory.LazyFunction(date.today)
    salary = Decimal("500000.00")
    is_active = True


class LeaveTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeaveType

    name = factory.Sequence(lambda n: f"Leave Type {n}")
    days_allowed = 21
    is_paid = True
    is_active = True


class LeaveRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeaveRequest

    employee = factory.SubFactory(EmployeeFactory)
    leave_type = factory.SubFactory(LeaveTypeFactory)
    start_date = factory.LazyFunction(date.today)
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=5))
    days = 5
    reason = "Personal reasons."
    status = "pending"


class AttendanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Attendance

    employee = factory.SubFactory(EmployeeFactory)
    date = factory.LazyFunction(date.today)
    check_in = factory.LazyFunction(lambda: __import__("datetime").time(8, 0))
    status = "present"


class PayrollFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payroll

    employee = factory.SubFactory(EmployeeFactory)
    month = 1
    year = 2025
    basic_salary = Decimal("500000.00")
    allowances = Decimal("125000.00")
    deductions = Decimal("86875.00")
    net_salary = Decimal("538125.00")
    payment_status = "pending"
