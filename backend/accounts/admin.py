from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import PasswordReset, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "user_type", "is_active", "is_staff", "created_at")
    list_filter = ("user_type", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra Info", {"fields": ("user_type", "phone", "address", "photo")}),
    )


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "expires_at")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
