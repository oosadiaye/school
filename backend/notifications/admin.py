from django.contrib import admin

from .models import Announcement, EmailTemplate, Notification, SMSTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "user__username")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "subject")
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(SMSTemplate)
class SMSTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    readonly_fields = ("created_at",)
    ordering = ("name",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "target_audience", "is_published", "created_by", "created_at")
    list_filter = ("target_audience", "is_published")
    search_fields = ("title",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
