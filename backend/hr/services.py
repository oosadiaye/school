"""Business logic for the HR app."""
from __future__ import annotations

from datetime import date, time
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone

from hr.exceptions import AlreadyCheckedIn, InsufficientLeaveBalance, NotCheckedIn
from hr.models import Attendance, Department, Employee, LeaveRequest, LeaveType, Payroll


class EmployeeService:
    """Handles employee onboarding and department transfers."""

    @staticmethod
    @transaction.atomic
    def onboard(
        user,
        department: Department,
        designation: str,
        *,
        employee_id: str | None = None,
        employment_type: str = "permanent",
        hire_date: date | None = None,
        salary: Decimal | None = None,
        by=None,
    ) -> Employee:
        """Create an Employee record for a user.

        Args:
            user: the auth user to link.
            department: target department.
            designation: one of Employee.DESIGNATION_CHOICES values.
            employee_id: unique employee code; auto-generated if omitted.
            employment_type: one of Employee.EMPLOYMENT_TYPES values.
            hire_date: defaults to today.
            salary: optional starting salary.
            by: user performing the action (unused, kept for audit trail).
        """
        if hire_date is None:
            hire_date = date.today()

        if employee_id is None:
            last = Employee.objects.order_by("-pk").first()
            next_num = (last.pk + 1) if last else 1
            employee_id = f"EMP{next_num:05d}"

        return Employee.objects.create(
            user=user,
            employee_id=employee_id,
            department=department,
            designation=designation,
            employment_type=employment_type,
            hire_date=hire_date,
            salary=salary or Decimal("0.00"),
            is_active=True,
        )

    @staticmethod
    @transaction.atomic
    def transfer_department(
        employee: Employee,
        new_department: Department,
        by=None,
    ) -> Employee:
        """Move an employee to a different department."""
        employee.department = new_department
        employee.save(update_fields=["department", "updated_at"])
        return employee


class LeaveService:
    """Handles leave requests, approvals, rejections, and balance queries."""

    @staticmethod
    def get_leave_balance(employee: Employee, leave_type: LeaveType, year: int) -> int:
        """Return remaining leave days for an employee in the given year.

        Calculation: leave_type.days_allowed - approved days used this year.
        """
        used = (
            LeaveRequest.objects.filter(
                employee=employee,
                leave_type=leave_type,
                status="approved",
                start_date__year=year,
            ).aggregate(total=Sum("days"))["total"]
            or 0
        )
        return leave_type.days_allowed - used

    @staticmethod
    @transaction.atomic
    def request_leave(
        employee: Employee,
        leave_type: LeaveType,
        start_date: date,
        end_date: date,
        reason: str,
    ) -> LeaveRequest:
        """Create a pending leave request after validating balance.

        Raises:
            ValueError: if end_date <= start_date.
            InsufficientLeaveBalance: if remaining balance < days requested.
        """
        if end_date <= start_date:
            raise ValueError("end_date must be after start_date.")

        days_requested = (end_date - start_date).days
        balance = LeaveService.get_leave_balance(
            employee, leave_type, start_date.year
        )
        if balance < days_requested:
            raise InsufficientLeaveBalance(available=balance, requested=days_requested)

        return LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days=days_requested,
            reason=reason,
            status="pending",
        )

    @staticmethod
    @transaction.atomic
    def approve_leave(leave_request: LeaveRequest, by) -> LeaveRequest:
        """Mark a leave request as approved."""
        leave_request.status = "approved"
        leave_request.approved_by = by
        leave_request.approved_date = timezone.now()
        leave_request.save(update_fields=["status", "approved_by", "approved_date"])
        return leave_request

    @staticmethod
    @transaction.atomic
    def reject_leave(leave_request: LeaveRequest, reason: str, by) -> LeaveRequest:
        """Mark a leave request as rejected."""
        leave_request.status = "rejected"
        leave_request.approved_by = by
        leave_request.approved_date = timezone.now()
        leave_request.save(update_fields=["status", "approved_by", "approved_date"])
        return leave_request


class PayrollService:
    """Handles payroll generation."""

    # Default percentages (kept simple; override via settings in production)
    TAX_RATE = Decimal("0.075")
    PENSION_RATE = Decimal("0.08")
    ALLOWANCE_RATE = Decimal("0.25")

    @classmethod
    @transaction.atomic
    def generate_payroll(
        cls,
        employee: Employee,
        month: int,
        year: int,
        by=None,
    ) -> Payroll:
        """Generate a single payroll record for an employee."""
        basic = employee.salary or Decimal("0.00")
        allowances = (basic * cls.ALLOWANCE_RATE).quantize(Decimal("0.01"))
        gross = basic + allowances

        tax = (gross * cls.TAX_RATE).quantize(Decimal("0.01"))
        pension = (basic * cls.PENSION_RATE).quantize(Decimal("0.01"))
        deductions = tax + pension
        net = gross - deductions

        return Payroll.objects.create(
            employee=employee,
            month=month,
            year=year,
            basic_salary=basic,
            allowances=allowances,
            deductions=deductions,
            net_salary=net,
            payment_status="pending",
        )

    @classmethod
    @transaction.atomic
    def generate_bulk(cls, month: int, year: int, by=None) -> list[Payroll]:
        """Generate payroll for all active employees."""
        employees = Employee.objects.filter(is_active=True)
        return [
            cls.generate_payroll(emp, month, year, by=by)
            for emp in employees
        ]


class AttendanceService:
    """Handles daily check-in / check-out."""

    @staticmethod
    @transaction.atomic
    def check_in(
        employee: Employee,
        check_in_time: time | None = None,
    ) -> Attendance:
        """Record a check-in for today.

        Raises:
            AlreadyCheckedIn: if an open attendance record already exists today.
        """
        today = date.today()

        if Attendance.objects.filter(employee=employee, date=today).exists():
            raise AlreadyCheckedIn(employee.employee_id)

        if check_in_time is None:
            check_in_time = timezone.localtime().time()

        return Attendance.objects.create(
            employee=employee,
            date=today,
            check_in=check_in_time,
            status="present",
        )

    @staticmethod
    @transaction.atomic
    def check_out(
        employee: Employee,
        check_out_time: time | None = None,
    ) -> Attendance:
        """Record a check-out for today.

        Raises:
            NotCheckedIn: if no open attendance record exists today.
        """
        today = date.today()

        try:
            attendance = Attendance.objects.get(
                employee=employee,
                date=today,
                check_out__isnull=True,
            )
        except Attendance.DoesNotExist:
            raise NotCheckedIn(employee.employee_id)

        if check_out_time is None:
            check_out_time = timezone.localtime().time()

        attendance.check_out = check_out_time
        attendance.save(update_fields=["check_out"])
        return attendance
