from rest_framework import serializers
from .models import Department, Employee, LeaveType, LeaveRequest, Attendance, Payroll

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head', 'description']

class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_name', 'employee_id', 'department', 'department_name', 'designation', 'employment_type', 'hire_date', 'salary', 'is_active']

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ['id', 'name', 'days_allowed', 'is_paid', 'is_active']

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'employee_name', 'leave_type', 'leave_type_name', 'start_date', 'end_date', 'days', 'reason', 'status']

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_name', 'date', 'check_in', 'check_out', 'status', 'notes']

class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    class Meta:
        model = Payroll
        fields = ['id', 'employee', 'employee_name', 'month', 'year', 'basic_salary', 'allowances', 'deductions', 'net_salary', 'payment_status']
