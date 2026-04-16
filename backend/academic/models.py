from django.db import models
from django.conf import settings
from students.models import Programme


class AcademicSession(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_registration_open = models.BooleanField(default=False)
    is_exam_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academic_sessions'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicSession.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)


class Semester(models.Model):
    SEMESTER_CHOICES = [
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
        ('rain', 'Rain Semester'),
        ('harmattan', 'Harmattan Semester'),
    ]
    
    name = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='semesters')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    registration_deadline = models.DateField(null=True, blank=True)
    exam_deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'semesters'
        ordering = ['session', 'name']
        unique_together = ['session', 'name']

    def __str__(self):
        return f"{self.name.title()} - {self.session.name}"


class Course(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=200)
    credit_units = models.PositiveIntegerField(default=3)
    level = models.CharField(max_length=10)
    semester = models.CharField(max_length=20, choices=Semester.SEMESTER_CHOICES, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        ordering = ['code']
        unique_together = ['programme', 'code', 'level']

    def __str__(self):
        return f"{self.code} - {self.name}"


class CourseAllocation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='allocations')
    lecturer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='allocated_courses'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'course_allocations'
        unique_together = ['course', 'semester']

    def __str__(self):
        return f"{self.course.code} - {self.lecturer.username}"


class CourseRegistration(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='course_registrations'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('registered', 'Registered'),
            ('dropped', 'Dropped'),
            ('completed', 'Completed'),
        ],
        default='registered'
    )

    class Meta:
        db_table = 'course_registrations'
        unique_together = ['student', 'course', 'semester']
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['semester', 'status']),
            models.Index(fields=['student', 'semester']),
        ]

    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}"


class Attendance(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total_classes = models.PositiveIntegerField(default=0)
    attended_classes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendances'
        unique_together = ['student', 'course', 'semester']
        indexes = [
            models.Index(fields=['student', 'course', 'semester']),
        ]

    @property
    def attendance_percentage(self):
        if self.total_classes == 0:
            return 0
        return (self.attended_classes / self.total_classes) * 100


class Result(models.Model):
    GRADE_CHOICES = [
        ('A', 'A (70-100)'),
        ('B', 'B (60-69)'),
        ('C', 'C (50-59)'),
        ('D', 'D (45-49)'),
        ('E', 'E (40-44)'),
        ('F', 'F (0-39)'),
    ]
    
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='results'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='results')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    ca_score = models.FloatField(null=True, blank=True)
    exam_score = models.FloatField(null=True, blank=True)
    total_score = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    grade_point = models.FloatField(null=True, blank=True)
    remark = models.CharField(max_length=50, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='entered_results'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'results'
        unique_together = ['student', 'course', 'semester']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'semester']),
            models.Index(fields=['course', 'semester']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}: {self.grade}"

    def save(self, *args, **kwargs):
        if self.ca_score is not None and self.exam_score is not None:
            self.total_score = self.ca_score + self.exam_score
            self.grade = self.calculate_grade(self.total_score)
            self.grade_point = self.calculate_grade_point(self.grade)
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_grade(score):
        if score >= 70:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        elif score >= 45:
            return 'D'
        elif score >= 40:
            return 'E'
        return 'F'

    @staticmethod
    def calculate_grade_point(grade):
        grade_points = {'A': 4.0, 'B': 3.5, 'C': 3.0, 'D': 2.5, 'E': 2.0, 'F': 0.0}
        return grade_points.get(grade, 0.0)


class ExamSitting(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='exam_sittings'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    venue = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    invigilator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='invigilated_exams'
    )
    is_absent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'exam_sittings'
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.student.matric_number} - {self.course.code}"
