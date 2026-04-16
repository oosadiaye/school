"""Business logic for the hostel app."""
from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from hostel.exceptions import AlreadyAllocated, GenderMismatch, RoomFull
from hostel.models import HostelAssignment, HostelFee, Room, RoomChangeRequest
from students.models import Student


ACTIVE_STATUSES = ('pending', 'approved', 'checked_in')


class AllocationService:
    """Handles room assignment and deallocation."""

    @staticmethod
    @transaction.atomic
    def assign_room(
        student: Student,
        room: Room,
        session: str,
        by=None,
    ) -> HostelAssignment:
        """Assign a student to a room for a given session.

        Validates gender compatibility, room capacity, and duplicate
        assignment before creating the HostelAssignment and incrementing
        the room's current_occupancy.

        Raises:
            GenderMismatch: hostel type does not accept the student's gender.
            RoomFull: room has reached its capacity.
            AlreadyAllocated: student already has an active assignment this session.
        """
        hostel = room.hostel

        # --- Gender check ---
        if hostel.hostel_type != 'mixed':
            student_gender = getattr(student, 'gender', '') or ''
            if student_gender and hostel.hostel_type != student_gender:
                raise GenderMismatch(hostel.hostel_type, student_gender)

        # --- Capacity check (lock the row) ---
        room = Room.objects.select_for_update().get(pk=room.pk)
        if room.current_occupancy >= room.capacity:
            raise RoomFull(room.room_number, room.capacity)

        # --- Duplicate assignment check ---
        if HostelAssignment.objects.filter(
            student=student,
            session=session,
            status__in=ACTIVE_STATUSES,
        ).exists():
            raise AlreadyAllocated(student.matric_number, session)

        # --- Create assignment ---
        assignment = HostelAssignment.objects.create(
            student=student,
            room=room,
            session=session,
            status='approved',
            assigned_by=by,
        )

        # --- Increment occupancy ---
        Room.objects.filter(pk=room.pk).update(
            current_occupancy=F('current_occupancy') + 1,
        )
        room.refresh_from_db()

        return assignment

    @staticmethod
    @transaction.atomic
    def deallocate(assignment: HostelAssignment, by=None) -> None:
        """Deactivate an assignment and free the room capacity.

        Sets assignment status to 'checked_out' and decrements the room's
        current_occupancy.
        """
        room = Room.objects.select_for_update().get(pk=assignment.room_id)

        assignment.status = 'checked_out'
        assignment.check_out_date = timezone.now().date()
        assignment.save(update_fields=['status', 'check_out_date'])

        Room.objects.filter(pk=room.pk).update(
            current_occupancy=F('current_occupancy') - 1,
        )
        room.refresh_from_db()


class RoomChangeService:
    """Handles room change requests and approvals."""

    @staticmethod
    def request_change(
        assignment: HostelAssignment,
        desired_room: Room,
        reason: str,
        by=None,
    ) -> RoomChangeRequest:
        """Create a room change request for an existing assignment."""
        return RoomChangeRequest.objects.create(
            student=assignment.student,
            from_room=assignment.room,
            to_room=desired_room,
            reason=reason,
        )

    @staticmethod
    @transaction.atomic
    def approve_change(
        request: RoomChangeRequest,
        by=None,
    ) -> HostelAssignment:
        """Approve a room change request.

        Deallocates the old room, allocates the new room, and marks the
        change request as approved — all within a single transaction.

        Raises:
            RoomFull: if the desired room has no capacity.
            GenderMismatch: if the desired room's hostel is incompatible.
        """
        # Mark old assignment as checked_out
        old_assignment = HostelAssignment.objects.filter(
            student=request.student,
            room=request.from_room,
            status__in=ACTIVE_STATUSES,
        ).select_related('room').first()

        if old_assignment:
            AllocationService.deallocate(old_assignment, by=by)

        # Allocate the new room
        new_assignment = AllocationService.assign_room(
            student=request.student,
            room=request.to_room,
            session=old_assignment.session if old_assignment else '',
            by=by,
        )

        # Update the change request
        request.status = 'approved'
        request.processed_by = by
        request.processed_date = timezone.now()
        request.save(update_fields=['status', 'processed_by', 'processed_date'])

        return new_assignment


class FeeService:
    """Handles hostel fee generation."""

    @staticmethod
    def generate_hostel_fee(assignment: HostelAssignment, by=None) -> HostelFee:
        """Create or return a HostelFee for the assignment's hostel and session.

        Uses the room's price_per_bed as the amount and a default due date
        90 days from now.
        """
        import datetime

        fee, _created = HostelFee.objects.get_or_create(
            hostel=assignment.room.hostel,
            session=assignment.session,
            defaults={
                'amount': assignment.room.price_per_bed,
                'due_date': (timezone.now() + datetime.timedelta(days=90)).date(),
            },
        )
        return fee
