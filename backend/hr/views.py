from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Department, Employee, LeaveType, LeaveRequest, Attendance, Payroll
from .serializers import DepartmentSerializer, EmployeeSerializer, LeaveTypeSerializer, LeaveRequestSerializer, AttendanceSerializer, PayrollSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name', 'code']
    pagination_class = PageNumberPagination

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department').all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['department', 'designation', 'employment_type', 'is_active']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    pagination_class = PageNumberPagination

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee__user', 'leave_type', 'approved_by').all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'status', 'leave_type']
    pagination_class = PageNumberPagination

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee__user').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'date', 'status']
    pagination_class = PageNumberPagination

class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('employee__user', 'approved_by').all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'month', 'year', 'payment_status']
    pagination_class = PageNumberPagination
