from django.contrib import admin

from .models import (
    Accreditation,
    ComplianceChecklist,
    ComplianceItem,
    GraduationList,
    NUCReport,
)


@admin.register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    list_display = ("programme", "accreditation_status", "accreditation_date", "expiry_date")
    list_filter = ("accreditation_status",)
    search_fields = ("programme__name", "nuc_ref_number")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-accreditation_date",)


@admin.register(NUCReport)
class NUCReportAdmin(admin.ModelAdmin):
    list_display = ("title", "report_type", "session", "status", "created_at")
    list_filter = ("report_type", "session", "status")
    search_fields = ("title",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-submission_date",)


@admin.register(ComplianceChecklist)
class ComplianceChecklistAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(ComplianceItem)
class ComplianceItemAdmin(admin.ModelAdmin):
    list_display = ("checklist", "name", "is_completed", "completed_date")
    list_filter = ("is_completed",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(GraduationList)
class GraduationListAdmin(admin.ModelAdmin):
    list_display = ("programme", "session", "total_graduands", "nuc_verified")
    list_filter = ("session", "nuc_verified")
    search_fields = ("programme__name",)
    readonly_fields = ("created_at",)
    ordering = ("-session",)
