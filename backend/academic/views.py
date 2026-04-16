from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from students.models import Student
from .models import (
    AcademicSession, Semester, Course, CourseAllocation,
    CourseRegistration, Attendance, Result, ExamSitting,
)
from .serializers import (
    AcademicSessionSerializer, SemesterSerializer, CourseSerializer,
    CourseCreateSerializer, CourseAllocationSerializer,
    CourseRegistrationSerializer, AttendanceSerializer,
    ResultSerializer, ResultCreateSerializer, ExamSittingSerializer
)
from .services import (
    ExamSittingService,
    RegistrationService,
    ResultService,
    SessionService,
    SemesterService,
)


class AcademicSessionViewSet(viewsets.ModelViewSet):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_current']
    pagination_class = PageNumberPagination
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        session = SessionService.get_current()
        if not session:
            return Response({'error': 'No current session'}, status=404)
        return Response(self.get_serializer(session).data)


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.select_related('session').all()
    serializer_class = SemesterSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['session', 'is_active']
    pagination_class = PageNumberPagination
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        semester = SemesterService.get_active()
        if not semester:
            return Response({'error': 'No active semester'}, status=404)
        return Response(self.get_serializer(semester).data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('programme').all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'level', 'semester']
    search_fields = ['code', 'name']
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer
        return CourseSerializer


class CourseAllocationViewSet(viewsets.ModelViewSet):
    queryset = CourseAllocation.objects.select_related('course', 'lecturer', 'semester').all()
    serializer_class = CourseAllocationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['lecturer', 'semester', 'course']
    pagination_class = PageNumberPagination
    
    def perform_create(self, serializer):
        serializer.save(lecturer=self.request.user)


class CourseRegistrationViewSet(viewsets.ModelViewSet):
    queryset = CourseRegistration.objects.select_related(
        'student__user', 'course', 'semester', 'course__programme'
    ).all()
    serializer_class = CourseRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'semester', 'status']
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            try:
                student = user.student_profile
                return CourseRegistration.objects.select_related(
                    'student__user', 'course', 'semester', 'course__programme'
                ).filter(student=student)
            except Student.DoesNotExist:
                return CourseRegistration.objects.none()
        return super().get_queryset()
    
    def perform_create(self, serializer):
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def register_courses(self, request):
        student_id = request.data.get('student_id')
        semester_id = request.data.get('semester_id')
        course_ids = request.data.get('course_ids', [])

        if not all([student_id, semester_id, course_ids]):
            return Response(
                {'error': 'student_id, semester_id, and course_ids are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            semester = Semester.objects.select_related('session').get(id=semester_id)
        except Semester.DoesNotExist:
            return Response({'error': 'Semester not found'}, status=404)

        student = Student.objects.get(id=student_id)
        result = RegistrationService.register_courses_bulk(student, course_ids, semester)
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def my_courses(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=404)

        semester_id = request.query_params.get('semester_id')
        semester = None
        if semester_id:
            semester = Semester.objects.filter(id=semester_id).first()

        queryset = RegistrationService.get_student_courses(student, semester=semester)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'course', 'semester').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'course', 'semester']
    pagination_class = PageNumberPagination


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related('student__user', 'course', 'semester', 'entered_by').all()
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'course', 'semester', 'is_published']
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ResultCreateSerializer
        return ResultSerializer
    
    def perform_create(self, serializer):
        serializer.save(entered_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=404)

        semester_id = request.query_params.get('semester_id')
        semester = Semester.objects.filter(id=semester_id).first() if semester_id else None
        queryset = ResultService.get_student_results(student, semester=semester)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def calculate_gpa(self, request):
        student_id = request.query_params.get('student_id')
        semester_id = request.query_params.get('semester_id')

        if not student_id:
            return Response({'error': 'student_id is required'}, status=400)

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        semester = Semester.objects.filter(id=semester_id).first() if semester_id else None
        data = ResultService.calculate_gpa_cgpa(student, semester=semester)
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        result = self.get_object()
        ResultService.publish_result(result, by=request.user)
        return Response({'message': 'Result published successfully'})


class ExamSittingViewSet(viewsets.ModelViewSet):
    queryset = ExamSitting.objects.select_related('student__user', 'course', 'semester', 'invigilator').all()
    serializer_class = ExamSittingSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'course', 'semester', 'date']
    pagination_class = PageNumberPagination
    
    @action(detail=False, methods=['post'])
    def generate_seating(self, request):
        course_id = request.data.get('course_id')
        semester_id = request.data.get('semester_id')
        venue = request.data.get('venue')

        if not all([course_id, semester_id, venue]):
            return Response(
                {'error': 'course_id, semester_id, and venue are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = Course.objects.get(id=course_id)
        semester = Semester.objects.get(id=semester_id)
        sittings = ExamSittingService.generate_seating_for_course(
            course=course,
            semester=semester,
            venue=venue,
            exam_date=request.data.get('date'),
            exam_time=request.data.get('time', '09:00'),
        )
        return Response({
            'message': f'{len(sittings)} exam sittings generated',
            'count': len(sittings),
        })
