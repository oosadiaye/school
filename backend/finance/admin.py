from django.contrib import admin

from .models import (
    FeeStructure,
    FeeType,
    FeeWaiver,
    InstallmentPayment,
    InstallmentPlan,
    Invoice,
    Payment,
    PaymentReminder,
    Scholarship,
    StudentScholarship,
)


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("programme", "fee_type", "amount", "level", "session", "is_mandatory")
    list_filter = ("session", "level", "programme", "is_mandatory")
    search_fields = ("programme__name",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_structure", "amount", "balance", "status", "due_date")
    list_filter = ("status", "due_date")
    search_fields = ("student__matric_number",)
    readonly_fields = ("generated_at", "updated_at")
    ordering = ("-generated_at",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("student", "invoice", "amount", "status", "payment_method", "transaction_id", "payment_date")
    list_filter = ("status", "payment_method")
    search_fields = ("transaction_id", "reference")
    readonly_fields = ("payment_date", "created_at")
    ordering = ("-payment_date",)


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "fee_structure", "number_of_installments", "is_active")
    list_filter = ("is_active",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ("installment_plan", "invoice", "installment_number", "amount", "due_date", "is_paid")
    list_filter = ("is_paid",)
    ordering = ("installment_number",)


@admin.register(FeeWaiver)
class FeeWaiverAdmin(admin.ModelAdmin):
    list_display = ("student", "invoice", "waiver_type", "amount", "percentage", "is_approved")
    list_filter = ("is_approved", "waiver_type")
    search_fields = ("student__matric_number",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(StudentScholarship)
class StudentScholarshipAdmin(admin.ModelAdmin):
    list_display = ("student", "scholarship", "session", "is_active")
    list_filter = ("is_active",)
    search_fields = ("student__matric_number",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ("invoice", "reminder_date", "is_sent", "sent_at")
    list_filter = ("is_sent",)
    readonly_fields = ("created_at",)
    ordering = ("reminder_date",)
