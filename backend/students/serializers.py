from datetime import date

from rest_framework import serializers
from .models import Faculty, Department, Programme, Student
from accounts.serializers import UserSerializer


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'code', 'dean', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'faculty', 'faculty_name', 'hod', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProgrammeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    faculty_name = serializers.CharField(source='department.faculty.name', read_only=True)
    
    class Meta:
        model = Programme
        fields = ['id', 'name', 'code', 'department', 'department_name', 
                  'faculty_name', 'degree_type', 'duration_years', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    department_name = serializers.CharField(source='programme.department.name', read_only=True)
    faculty_name = serializers.CharField(source='programme.department.faculty.name', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'user', 'matric_number', 'programme', 'programme_name',
            'department_name', 'faculty_name', 'level', 'status',
            'jamb_number', 'admission_year', 'expected_graduation_year',
            'date_of_birth', 'place_of_birth', 'state_of_origin', 'lga',
            'guardian_name', 'guardian_phone', 'guardian_address', 
            'guardian_relationship', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'matric_number', 'created_at', 'updated_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'phone',
            'programme', 'level', 'jamb_number', 'admission_year',
            'date_of_birth', 'place_of_birth', 'state_of_origin', 'lga',
            'guardian_name', 'guardian_phone', 'guardian_address', 'guardian_relationship'
        ]

    def validate_date_of_birth(self, value):
        if value is None:
            return value
        today = date.today()
        if value >= today:
            raise serializers.ValidationError('Date of birth must be in the past.')
        age = (today - value).days / 365.25
        if age < 10:
            raise serializers.ValidationError('Student must be at least 10 years old.')
        return value

    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'user_type': 'student',
        }
        user_data['phone'] = validated_data.pop('phone', '')
        
        user = User.objects.create_user(**user_data)
        
        validated_data['user'] = user
        validated_data['admission_year'] = validated_data.get('admission_year', 2024)
        
        student = Student.objects.create(**validated_data)
        return student
