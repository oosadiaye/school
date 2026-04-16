from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator
from .models import (
    AcademicSession, Semester, Course, CourseAllocation,
    CourseRegistration, Attendance, Result, ExamSitting
)


class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSession
        fields = ['id', 'name', 'start_date', 'end_date', 'is_current', 
                  'is_registration_open', 'is_exam_enabled', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SemesterSerializer(serializers.ModelSerializer):
    session_name = serializers.CharField(source='session.name', read_only=True)
    
    class Meta:
        model = Semester
        fields = ['id', 'name', 'session', 'session_name', 'start_date', 'end_date',
                  'is_active', 'registration_deadline', 'exam_deadline', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'programme', 'programme_name', 'code', 'name', 
                  'credit_units', 'level', 'semester', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['programme', 'code', 'name', 'credit_units', 'level', 'semester', 'description']


class CourseAllocationSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    lecturer_name = serializers.CharField(source='lecturer.get_full_name', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)
    
    class Meta:
        model = CourseAllocation
        fields = ['id', 'course', 'course_name', 'course_code', 'lecturer', 
                  'lecturer_name', 'semester', 'semester_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseRegistrationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    semester_name = serializers.CharField(source='semester.name', read_only=True)

    class Meta:
        model = CourseRegistration
        fields = ['id', 'student', 'student_name', 'student_matric', 'course',
                  'course_name', 'course_code', 'semester', 'semester_name',
                  'registration_date', 'status']
        read_only_fields = ['id', 'registration_date']

    def validate_semester(self, value):
        if not value.is_active:
            raise serializers.ValidationError('Course registration is only allowed in an active semester.')
        return value


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    attendance_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'student_matric', 'course', 
                  'course_name', 'course_code', 'semester', 'total_classes', 
                  'attended_classes', 'attendance_percentage', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    entered_by_name = serializers.CharField(source='entered_by.get_full_name', read_only=True)
    
    class Meta:
        model = Result
        fields = ['id', 'student', 'student_name', 'student_matric', 'course', 
                  'course_name', 'course_code', 'semester', 'ca_score', 'exam_score',
                  'total_score', 'grade', 'grade_point', 'remark', 'entered_by',
                  'entered_by_name', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResultCreateSerializer(serializers.ModelSerializer):
    ca_score = serializers.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
    )
    exam_score = serializers.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(60)],
    )

    class Meta:
        model = Result
        fields = ['student', 'course', 'semester', 'ca_score', 'exam_score', 'remark']

    def validate(self, data):
        ca = data.get('ca_score', 0)
        exam = data.get('exam_score', 0)
        if ca + exam > 100:
            raise serializers.ValidationError({
                'exam_score': 'CA + Exam scores cannot exceed 100.'
            })
        return data


class ExamSittingSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    invigilator_name = serializers.CharField(source='invigilator.get_full_name', read_only=True)
    
    class Meta:
        model = ExamSitting
        fields = ['id', 'student', 'student_name', 'student_matric', 'course', 
                  'course_name', 'course_code', 'semester', 'venue', 'seat_number',
                  'date', 'time', 'invigilator', 'invigilator_name', 'is_absent', 'notes']
        read_only_fields = ['id']


class StudentResultSerializer(serializers.Serializer):
    course_code = serializers.CharField()
    course_name = serializers.CharField()
    credit_units = serializers.IntegerField()
    grade = serializers.CharField()
    grade_point = serializers.FloatField()
    semester = serializers.CharField()
    session = serializers.CharField()


class StudentTranscriptSerializer(serializers.Serializer):
    student_name = serializers.CharField()
    matric_number = serializers.CharField()
    programme = serializers.CharField()
    level = serializers.CharField()
    results = StudentResultSerializer(many=True)
    gpa = serializers.FloatField()
    cgpa = serializers.FloatField()
