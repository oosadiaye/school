from django.contrib import admin

from .models import Hostel, HostelAssignment, HostelFee, Room, RoomChangeRequest


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ("name", "hostel_type", "total_rooms", "capacity", "is_active")
    list_filter = ("hostel_type", "is_active")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "hostel", "room_type", "capacity", "current_occupancy", "is_available")
    list_filter = ("hostel", "room_type", "is_available")
    search_fields = ("room_number",)
    readonly_fields = ("created_at",)
    ordering = ("hostel", "room_number")


@admin.register(HostelAssignment)
class HostelAssignmentAdmin(admin.ModelAdmin):
    list_display = ("student", "room", "session", "status", "assigned_date")
    list_filter = ("status", "session")
    search_fields = ("student__matric_number",)
    readonly_fields = ("assigned_date", "created_at")
    ordering = ("-assigned_date",)


@admin.register(HostelFee)
class HostelFeeAdmin(admin.ModelAdmin):
    list_display = ("hostel", "session", "amount", "is_active")
    list_filter = ("is_active", "session")
    readonly_fields = ("created_at",)
    ordering = ("-session",)


@admin.register(RoomChangeRequest)
class RoomChangeRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "from_room", "to_room", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__matric_number",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
