from django.contrib import admin

from .models import Department, Faculty, Programme, Student


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "dean")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "faculty", "hod")
    list_filter = ("faculty",)
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "degree_type", "duration_years")
    list_filter = ("degree_type", "department")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("matric_number", "user", "programme", "level", "status")
    list_filter = ("status", "level", "programme")
    search_fields = ("matric_number", "user__username", "user__first_name", "user__last_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-admission_year", "matric_number")
