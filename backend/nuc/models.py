from django.db import models
from students.models import Programme


class Accreditation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accredited', 'Accredited'),
        ('probation', 'Probation'),
        ('denied', 'Denied'),
    ]
    
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='accreditations')
    accreditation_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    accreditation_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    nuc_ref_number = models.CharField(max_length=50, blank=True)
    visit_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accreditations'
        ordering = ['-accreditation_date']

    def __str__(self):
        return f"{self.programme.name} - {self.accreditation_status}"


class NUCReport(models.Model):
    REPORT_TYPES = [
        ('statistical', 'Statistical Digest'),
        ('compliance', 'Compliance Report'),
        ('accreditation', 'Accreditation Report'),
        ('annual', 'Annual Report'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    session = models.CharField(max_length=20)
    submission_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='draft')
    report_file = models.FileField(upload_to='nuc_reports/', blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nuc_reports'
        ordering = ['-submission_date']

    def __str__(self):
        return self.title


class ComplianceChecklist(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_checklists'
        ordering = ['name']

    def __str__(self):
        return self.name


class ComplianceItem(models.Model):
    checklist = models.ForeignKey(ComplianceChecklist, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    completed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'compliance_items'
        ordering = ['name']

    def __str__(self):
        return self.name


class GraduationList(models.Model):
    session = models.CharField(max_length=20)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='graduations')
    total_graduands = models.PositiveIntegerField(default=0)
    first_class = models.PositiveIntegerField(default=0)
    second_class_upper = models.PositiveIntegerField(default=0)
    second_class_lower = models.PositiveIntegerField(default=0)
    third_class = models.PositiveIntegerField(default=0)
    pass_class = models.PositiveIntegerField(default=0)
    submission_date = models.DateField(null=True, blank=True)
    nuc_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'graduation_lists'
        ordering = ['-session']

    def __str__(self):
        return f"Graduation {self.session} - {self.programme.name}"
