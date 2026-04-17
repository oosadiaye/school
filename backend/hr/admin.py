from django.contrib import admin

from .models import Attendance, Department, Employee, LeaveRequest, LeaveType, Payroll


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "user", "department", "designation", "employment_type", "is_active")
    list_filter = ("is_active", "department", "designation", "employment_type")
    search_fields = ("employee_id", "user__username", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-hire_date",)


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "days_allowed", "is_paid", "is_active")
    list_filter = ("is_active", "is_paid")
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "start_date", "end_date", "days", "status")
    list_filter = ("status", "leave_type")
    search_fields = ("employee__user__username", "employee__employee_id")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "check_in", "check_out", "status")
    list_filter = ("status", "date")
    search_fields = ("employee__user__username", "employee__employee_id")
    readonly_fields = ("created_at",)
    ordering = ("-date",)


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "year", "basic_salary", "net_salary", "payment_status")
    list_filter = ("payment_status", "month", "year")
    search_fields = ("employee__user__username", "employee__employee_id")
    readonly_fields = ("created_at",)
    ordering = ("-year", "-month")
