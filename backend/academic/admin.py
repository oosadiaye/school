from django.contrib import admin

from .models import (
    AcademicSession,
    Attendance,
    Course,
    CourseAllocation,
    CourseRegistration,
    ExamSitting,
    Result,
    Semester,
)


@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_current", "is_registration_open", "is_exam_enabled", "start_date", "end_date")
    list_filter = ("is_current", "is_registration_open")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start_date",)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ("name", "session", "is_active", "start_date", "end_date")
    list_filter = ("is_active", "session")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("session", "name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "programme", "credit_units", "level", "semester")
    list_filter = ("level", "semester", "programme")
    search_fields = ("code", "name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("code",)


@admin.register(CourseAllocation)
class CourseAllocationAdmin(admin.ModelAdmin):
    list_display = ("course", "lecturer", "semester")
    list_filter = ("semester",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "status", "registration_date")
    list_filter = ("status", "semester")
    search_fields = ("student__matric_number",)
    readonly_fields = ("registration_date",)
    ordering = ("-registration_date",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "total_classes", "attended_classes")
    list_filter = ("semester",)
    search_fields = ("student__matric_number",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "ca_score", "exam_score", "grade", "grade_point", "is_published")
    list_filter = ("is_published", "semester", "grade")
    search_fields = ("student__matric_number",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(ExamSitting)
class ExamSittingAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "semester", "venue", "seat_number", "date", "is_absent")
    list_filter = ("semester", "is_absent")
    search_fields = ("student__matric_number", "seat_number")
    ordering = ("date", "time")
