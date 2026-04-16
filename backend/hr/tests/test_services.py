"""Tests for HR service layer."""
from datetime import date, timedelta, time
from decimal import Decimal

import pytest

from hr.exceptions import AlreadyCheckedIn, InsufficientLeaveBalance, NotCheckedIn
from hr.services import AttendanceService, EmployeeService, LeaveService, PayrollService
from hr.tests.factories import (
    DepartmentFactory,
    EmployeeFactory,
    LeaveRequestFactory,
    LeaveTypeFactory,
)
from accounts.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# EmployeeService
# ---------------------------------------------------------------------------

class TestEmployeeService:

    def test_onboard_creates_employee(self):
        user = UserFactory(user_type="staff")
        dept = DepartmentFactory()

        employee = EmployeeService.onboard(
            user=user,
            department=dept,
            designation="lecturer",
        )

        assert employee.pk is not None
        assert employee.user == user
        assert employee.department == dept
        assert employee.designation == "lecturer"
        assert employee.is_active is True

    def test_transfer_department_updates_department(self):
        employee = EmployeeFactory()
        new_dept = DepartmentFactory(name="New Dept", code="NEW001")

        updated = EmployeeService.transfer_department(employee, new_dept)

        assert updated.department == new_dept


# ---------------------------------------------------------------------------
# LeaveService
# ---------------------------------------------------------------------------

class TestLeaveService:

    def test_request_leave_raises_insufficient_balance(self):
        """Requesting more days than the balance should raise."""
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory(days_allowed=5)
        start = date(2025, 6, 1)
        end = date(2025, 6, 15)  # 14 days, allowance is 5

        with pytest.raises(InsufficientLeaveBalance):
            LeaveService.request_leave(
                employee=employee,
                leave_type=leave_type,
                start_date=start,
                end_date=end,
                reason="Holiday",
            )

    def test_request_leave_validates_dates(self):
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory()

        with pytest.raises(ValueError, match="end_date must be after start_date"):
            LeaveService.request_leave(
                employee=employee,
                leave_type=leave_type,
                start_date=date(2025, 6, 10),
                end_date=date(2025, 6, 5),
                reason="Backwards dates",
            )

    def test_approve_leave_updates_status(self):
        leave_req = LeaveRequestFactory(status="pending")
        approver = UserFactory(user_type="admin")

        result = LeaveService.approve_leave(leave_req, by=approver)

        assert result.status == "approved"
        assert result.approved_by == approver
        assert result.approved_date is not None

    def test_reject_leave_does_not_affect_balance(self):
        """Rejected leave should not count against balance."""
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory(days_allowed=10)

        # Create a rejected request
        LeaveRequestFactory(
            employee=employee,
            leave_type=leave_type,
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 6),
            days=5,
            status="rejected",
        )

        balance = LeaveService.get_leave_balance(employee, leave_type, 2025)
        assert balance == 10  # rejected leave should not reduce balance

    def test_get_leave_balance_calculates_correctly(self):
        employee = EmployeeFactory()
        leave_type = LeaveTypeFactory(days_allowed=21)

        # Use 7 days (approved)
        LeaveRequestFactory(
            employee=employee,
            leave_type=leave_type,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 8),
            days=7,
            status="approved",
        )

        balance = LeaveService.get_leave_balance(employee, leave_type, 2025)
        assert balance == 14


# ---------------------------------------------------------------------------
# PayrollService
# ---------------------------------------------------------------------------

class TestPayrollService:

    def test_generate_payroll_calculates_net(self):
        employee = EmployeeFactory(salary=Decimal("500000.00"))

        payroll = PayrollService.generate_payroll(employee, month=1, year=2025)

        # basic=500000, allowances=125000 (25%), gross=625000
        # tax=46875 (7.5% of gross), pension=40000 (8% of basic)
        # deductions=86875, net=538125
        assert payroll.basic_salary == Decimal("500000.00")
        assert payroll.allowances == Decimal("125000.00")
        assert payroll.deductions == Decimal("86875.00")
        assert payroll.net_salary == Decimal("538125.00")
        assert payroll.payment_status == "pending"


# ---------------------------------------------------------------------------
# AttendanceService
# ---------------------------------------------------------------------------

class TestAttendanceService:

    def test_check_in_creates_record(self):
        employee = EmployeeFactory()

        attendance = AttendanceService.check_in(employee, check_in_time=time(8, 0))

        assert attendance.pk is not None
        assert attendance.employee == employee
        assert attendance.date == date.today()
        assert attendance.check_in == time(8, 0)
        assert attendance.status == "present"

    def test_check_in_raises_if_already_checked_in(self):
        employee = EmployeeFactory()
        AttendanceService.check_in(employee, check_in_time=time(8, 0))

        with pytest.raises(AlreadyCheckedIn):
            AttendanceService.check_in(employee, check_in_time=time(9, 0))

    def test_check_out_updates_record(self):
        employee = EmployeeFactory()
        AttendanceService.check_in(employee, check_in_time=time(8, 0))

        attendance = AttendanceService.check_out(employee, check_out_time=time(17, 0))

        assert attendance.check_out == time(17, 0)

    def test_check_out_raises_not_checked_in(self):
        employee = EmployeeFactory()

        with pytest.raises(NotCheckedIn):
            AttendanceService.check_out(employee, check_out_time=time(17, 0))
