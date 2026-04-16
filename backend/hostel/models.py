from django.db import models
from django.conf import settings


class Hostel(models.Model):
    TYPE_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('mixed', 'Mixed'),
    ]
    
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    hostel_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    address = models.TextField(blank=True)
    warden = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='warden_of')
    total_rooms = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hostels'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    ROOM_TYPES = [
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
        ('dormitory', 'Dormitory'),
    ]
    
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField(default=2)
    current_occupancy = models.PositiveIntegerField(default=0)
    price_per_bed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rooms'
        unique_together = ['hostel', 'room_number']
        ordering = ['hostel', 'room_number']

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"


class HostelAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_assignments')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='assignments')
    session = models.CharField(max_length=20)
    bed_number = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    assigned_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hostel_assignments'
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.student.matric_number} - {self.room.hostel.name}"


class HostelFee(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='fees')
    session = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'hostel_fees'
        unique_together = ['hostel', 'session']

    def __str__(self):
        return f"{self.hostel.name} - {self.session}: {self.amount}"


class RoomChangeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='room_change_requests')
    from_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='change_from')
    to_room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='change_to')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    processed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'room_change_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.matric_number} - Room Change Request"
