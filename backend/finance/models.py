from django.db import models
from django.conf import settings
from students.models import Programme


class FeeType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fee_types'
        ordering = ['name']

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type = models.ForeignKey(FeeType, on_delete=models.CASCADE, related_name='fee_structures')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    level = models.CharField(max_length=10)
    session = models.CharField(max_length=20)
    is_mandatory = models.BooleanField(default=True)
    due_date = models.DateField(null=True, blank=True)
    auto_generate = models.BooleanField(default=True, help_text="Auto-generate invoice on student registration")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fee_structures'
        unique_together = ['programme', 'fee_type', 'level', 'session']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.programme.name} - {self.fee_type.name}: {self.amount}"


class InstallmentPlan(models.Model):
    name = models.CharField(max_length=100)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='installment_plans')
    number_of_installments = models.IntegerField(default=2)
    due_dates = models.JSONField(default=list, help_text="List of due dates for each installment")
    penalty_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Penalty for late payment")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'installment_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.number_of_installments} installments"


class InstallmentPayment(models.Model):
    installment_plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name='payments')
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='installments')
    installment_number = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateField(null=True, blank=True)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'installment_payments'
        ordering = ['installment_number']
        indexes = [
            models.Index(fields=['invoice', 'is_paid', 'installment_number']),
        ]

    def __str__(self):
        return f"Installment {self.installment_number} - {self.invoice.id}"


class FeeWaiver(models.Model):
    WAIVER_TYPES = [
        ('full', 'Full Waiver'),
        ('partial', 'Partial Waiver'),
        ('percentage', 'Percentage Waiver'),
    ]
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='fee_waivers')
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='waivers')
    waiver_type = models.CharField(max_length=20, choices=WAIVER_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentage waiver (0-100)")
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='approved_waivers')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'fee_waivers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Waiver for {self.invoice.id} - {self.amount}"


class Invoice(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('partially_paid', 'Partially Paid'),
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('waived', 'Waived'),
        ],
        default='pending'
    )
    due_date = models.DateField()
    generated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'invoices'
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['status', 'due_date']),
        ]

    def __str__(self):
        return f"Invoice {self.id} - {self.student.matric_number}"

    def save(self, *args, **kwargs):
        self.balance = self.amount - self.amount_paid
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partially_paid'
        super().save(*args, **kwargs)


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('bank_transfer', 'Bank Transfer'),
        ('online', 'Online Payment'),
        ('cash', 'Cash'),
        ('pos', 'POS'),
        ('ussd', 'USSD'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    reference = models.CharField(max_length=100, blank=True, db_index=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    channel = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['status', 'payment_date']),
        ]

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"


class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scholarships'
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentScholarship(models.Model):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='scholarships'
    )
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    session = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'student_scholarships'

    def __str__(self):
        return f"{self.student.matric_number} - {self.scholarship.name}"


class PaymentReminder(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='reminders')
    reminder_date = models.DateField()
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment_reminders'
        ordering = ['reminder_date']

    def __str__(self):
        return f"Reminder for Invoice {self.invoice.id}"
