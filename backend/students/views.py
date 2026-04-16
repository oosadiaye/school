from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Faculty, Department, Programme, Student
from .serializers import (
    FacultySerializer, DepartmentSerializer,
    ProgrammeSerializer, StudentSerializer, StudentCreateSerializer
)
from .services import (
    StudentService, FacultyService, DepartmentService, ProgrammeService,
)


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    filterset_fields = ['name', 'code']
    pagination_class = PageNumberPagination

    def perform_destroy(self, instance):
        FacultyService.safe_delete(instance, by=self.request.user)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('faculty').all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['faculty', 'name', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    pagination_class = PageNumberPagination

    def perform_destroy(self, instance):
        DepartmentService.safe_delete(instance, by=self.request.user)


class ProgrammeViewSet(viewsets.ModelViewSet):
    queryset = Programme.objects.select_related('department__faculty').all()
    serializer_class = ProgrammeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['department', 'department__faculty', 'degree_type']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    pagination_class = PageNumberPagination

    def perform_destroy(self, instance):
        ProgrammeService.safe_delete(instance, by=self.request.user)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'programme__department__faculty').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'level', 'status', 'admission_year']
    search_fields = ['matric_number', 'user__first_name', 'user__last_name', 'user__email', 'jamb_number']
    ordering_fields = ['matric_number', 'admission_year', 'created_at']
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    def get_queryset(self):
        return StudentService.filter_for_user(self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        student = StudentService.get_profile_for_user(request.user)
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        student = self.get_object()
        new_status = request.data.get('status')
        updated = StudentService.update_status(student, new_status, by=request.user)
        return Response(StudentSerializer(updated).data)
