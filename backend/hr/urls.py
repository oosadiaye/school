from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, EmployeeViewSet, LeaveTypeViewSet, LeaveRequestViewSet, AttendanceViewSet, PayrollViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'leave-types', LeaveTypeViewSet)
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'payrolls', PayrollViewSet)

urlpatterns = [path('', include(router.urls))]
