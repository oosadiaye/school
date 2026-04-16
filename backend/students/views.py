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


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    filterset_fields = ['name', 'code']
    pagination_class = PageNumberPagination


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('faculty').all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['faculty', 'name', 'code']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    pagination_class = PageNumberPagination


class ProgrammeViewSet(viewsets.ModelViewSet):
    queryset = Programme.objects.select_related('department__faculty').all()
    serializer_class = ProgrammeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['department', 'department__faculty', 'degree_type']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'created_at']
    pagination_class = PageNumberPagination


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
        user = self.request.user
        if user.user_type == 'student':
            return Student.objects.filter(user=user)
        return super().get_queryset()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        try:
            student = Student.objects.get(user=request.user)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        student = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Student.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        student.status = new_status
        student.save()
        return Response(StudentSerializer(student).data)
