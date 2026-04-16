from django.db import models
from django.conf import settings
from django.db import transaction


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    dean = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='dean_of_faculty'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'faculties'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='hod_of_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'departments'
        ordering = ['name']
        unique_together = ['faculty', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.faculty.code})"


class Programme(models.Model):
    DEGREE_CHOICES = [
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('phd', 'PhD'),
        ('nd', 'ND'),
        ('hnd', 'HND'),
        ('pgd', 'PGD'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programmes')
    degree_type = models.CharField(max_length=20, choices=DEGREE_CHOICES)
    duration_years = models.PositiveIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'programmes'
        ordering = ['name']
        unique_together = ['department', 'code']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('withdrawn', 'Withdrawn'),
        ('graduated', 'Graduated'),
        ('deferred', 'Deferred'),
    ]
    
    LEVELS = [
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level'),
        ('500', '500 Level'),
        ('600', '600 Level'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    matric_number = models.CharField(max_length=20, unique=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='students')
    level = models.CharField(max_length=10, choices=LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    jamb_number = models.CharField(max_length=20, blank=True, db_index=True)
    admission_year = models.PositiveIntegerField(db_index=True)
    expected_graduation_year = models.PositiveIntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female')],
        blank=True,
    )
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, blank=True)
    state_of_origin = models.CharField(max_length=50, blank=True, db_index=True)
    lga = models.CharField(max_length=100, blank=True)
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_address = models.TextField(blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'students'
        ordering = ['-admission_year', 'matric_number']
        indexes = [
            models.Index(fields=['programme', 'level']),
            models.Index(fields=['status', 'admission_year']),
        ]
    
    def __str__(self):
        return f"{self.matric_number} - {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.matric_number:
            year = self.admission_year
            prog_code = self.programme.code
            prefix = f"{year}/{prog_code}"
            
            with transaction.atomic():
                last_student = Student.objects.select_for_update().filter(
                    matric_number__startswith=prefix
                ).order_by('-matric_number').first()
                
                if last_student:
                    last_num = int(last_student.matric_number.split('/')[-1])
                    new_num = last_num + 1
                else:
                    new_num = 1
                
                self.matric_number = f"{prefix}/{new_num:04d}"
        
        if not self.expected_graduation_year:
            self.expected_graduation_year = self.admission_year + self.programme.duration_years
        
        super().save(*args, **kwargs)
