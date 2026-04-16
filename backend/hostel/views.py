from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Hostel, Room, HostelAssignment, HostelFee, RoomChangeRequest
from .serializers import HostelSerializer, RoomSerializer, HostelAssignmentSerializer, HostelFeeSerializer

class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.select_related('warden').all()
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name', 'gender']
    pagination_class = PageNumberPagination

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('hostel').all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['hostel', 'is_available', 'room_type']
    pagination_class = PageNumberPagination

class HostelAssignmentViewSet(viewsets.ModelViewSet):
    queryset = HostelAssignment.objects.select_related('student__user', 'room__hostel', 'assigned_by').all()
    serializer_class = HostelAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'room', 'status', 'session']
    pagination_class = PageNumberPagination

class HostelFeeViewSet(viewsets.ModelViewSet):
    queryset = HostelFee.objects.select_related('hostel').all()
    serializer_class = HostelFeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['hostel', 'session']
    pagination_class = PageNumberPagination
