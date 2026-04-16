from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .exceptions import AlreadyAllocated, GenderMismatch, RoomFull
from .models import Hostel, HostelAssignment, HostelFee, Room, RoomChangeRequest
from .serializers import (
    HostelAssignmentSerializer,
    HostelFeeSerializer,
    HostelSerializer,
    RoomSerializer,
)
from .services import AllocationService, FeeService, RoomChangeService


class HostelViewSet(viewsets.ModelViewSet):
    queryset = Hostel.objects.select_related('warden').all()
    serializer_class = HostelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name', 'hostel_type']
    pagination_class = PageNumberPagination


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.select_related('hostel').all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['hostel', 'is_available', 'room_type']
    pagination_class = PageNumberPagination


class HostelAssignmentViewSet(viewsets.ModelViewSet):
    queryset = HostelAssignment.objects.select_related(
        'student__user', 'room__hostel', 'assigned_by',
    ).all()
    serializer_class = HostelAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'room', 'status', 'session']
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        """Delegate creation to AllocationService for validation."""
        data = serializer.validated_data
        try:
            assignment = AllocationService.assign_room(
                student=data['student'],
                room=data['room'],
                session=data['session'],
                by=self.request.user,
            )
        except (GenderMismatch, RoomFull, AlreadyAllocated) as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': str(exc)})
        # Replace the serializer instance so the response uses the created object
        serializer.instance = assignment

    @action(detail=True, methods=['post'])
    def deallocate(self, request, pk=None):
        assignment = self.get_object()
        AllocationService.deallocate(assignment, by=request.user)
        return Response(
            HostelAssignmentSerializer(assignment).data,
            status=status.HTTP_200_OK,
        )


class HostelFeeViewSet(viewsets.ModelViewSet):
    queryset = HostelFee.objects.select_related('hostel').all()
    serializer_class = HostelFeeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['hostel', 'session']
    pagination_class = PageNumberPagination
