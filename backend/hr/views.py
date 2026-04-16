from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .exceptions import AlreadyCheckedIn, InsufficientLeaveBalance, NotCheckedIn
from .models import Department, Employee, LeaveType, LeaveRequest, Attendance, Payroll
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    LeaveTypeSerializer,
    LeaveRequestSerializer,
    AttendanceSerializer,
    PayrollSerializer,
)
from .services import AttendanceService, EmployeeService, LeaveService, PayrollService


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

    @action(detail=True, methods=['post'], url_path='transfer')
    def transfer_department(self, request, pk=None):
        employee = self.get_object()
        department_id = request.data.get('department')
        if not department_id:
            return Response(
                {'error': 'department is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            department = Department.objects.get(pk=department_id)
        except Department.DoesNotExist:
            return Response(
                {'error': 'Department not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        updated = EmployeeService.transfer_department(employee, department, by=request.user)
        return Response(EmployeeSerializer(updated).data)


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

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        leave_request = self.get_object()
        result = LeaveService.approve_leave(leave_request, by=request.user)
        return Response(LeaveRequestSerializer(result).data)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        leave_request = self.get_object()
        reason = request.data.get('reason', '')
        result = LeaveService.reject_leave(leave_request, reason=reason, by=request.user)
        return Response(LeaveRequestSerializer(result).data)


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee__user').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'date', 'status']
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        employee_id = request.data.get('employee')
        if not employee_id:
            return Response({'error': 'employee is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendance = AttendanceService.check_in(employee)
        except AlreadyCheckedIn as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        employee_id = request.data.get('employee')
        if not employee_id:
            return Response({'error': 'employee is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(pk=employee_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            attendance = AttendanceService.check_out(employee)
        except NotCheckedIn as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AttendanceSerializer(attendance).data)


class PayrollViewSet(viewsets.ModelViewSet):
    queryset = Payroll.objects.select_related('employee__user').all()
    serializer_class = PayrollSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['employee', 'month', 'year', 'payment_status']
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['post'], url_path='generate-bulk')
    def generate_bulk(self, request):
        month = request.data.get('month')
        year = request.data.get('year')
        if not month or not year:
            return Response(
                {'error': 'month and year are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payrolls = PayrollService.generate_bulk(
            month=int(month), year=int(year), by=request.user
        )
        return Response(
            PayrollSerializer(payrolls, many=True).data,
            status=status.HTTP_201_CREATED,
        )
