from rest_framework import serializers
from .models import Hostel, Room, HostelAssignment, HostelFee

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'code', 'hostel_type', 'address', 'warden', 'total_rooms', 'capacity', 'is_active']

class RoomSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'hostel', 'hostel_name', 'room_number', 'floor', 'room_type', 'capacity', 'current_occupancy', 'price_per_bed', 'is_available']

class HostelAssignmentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    room_name = serializers.CharField(source='room.room_number', read_only=True)
    class Meta:
        model = HostelAssignment
        fields = ['id', 'student', 'student_name', 'room', 'room_name', 'session', 'bed_number', 'status', 'check_in_date', 'check_out_date']

class HostelFeeSerializer(serializers.ModelSerializer):
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    class Meta:
        model = HostelFee
        fields = ['id', 'hostel', 'hostel_name', 'session', 'amount', 'due_date', 'is_active']
