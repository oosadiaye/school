"""Tests for hostel service layer."""
import pytest

from hostel.exceptions import AlreadyAllocated, GenderMismatch, RoomFull
from hostel.services import AllocationService, FeeService, RoomChangeService
from hostel.tests.factories import (
    HostelAssignmentFactory,
    HostelFactory,
    RoomFactory,
)
from students.tests.factories import StudentFactory


pytestmark = pytest.mark.django_db


class TestAllocationService:
    """Tests for AllocationService.assign_room and deallocate."""

    def test_assign_room_succeeds_when_capacity_available(self):
        """A student is assigned to a room with available capacity."""
        room = RoomFactory(capacity=2, current_occupancy=0)
        student = StudentFactory(gender='male')

        assignment = AllocationService.assign_room(
            student=student,
            room=room,
            session='2024/2025',
        )

        assert assignment.student == student
        assert assignment.room_id == room.pk
        assert assignment.status == 'approved'
        room.refresh_from_db()
        assert room.current_occupancy == 1

    def test_assign_room_raises_gender_mismatch(self):
        """A female student cannot be assigned to a male-only hostel."""
        hostel = HostelFactory(hostel_type='male')
        room = RoomFactory(hostel=hostel, capacity=2, current_occupancy=0)
        student = StudentFactory(gender='female')

        with pytest.raises(GenderMismatch):
            AllocationService.assign_room(
                student=student,
                room=room,
                session='2024/2025',
            )

    def test_assign_room_raises_room_full(self):
        """Assignment is refused when the room is at capacity."""
        room = RoomFactory(capacity=2, current_occupancy=2)
        student = StudentFactory(gender='male')

        with pytest.raises(RoomFull):
            AllocationService.assign_room(
                student=student,
                room=room,
                session='2024/2025',
            )

    def test_assign_room_raises_already_allocated(self):
        """A student with an active assignment for the session cannot get another."""
        room = RoomFactory(capacity=4, current_occupancy=0)
        student = StudentFactory(gender='male')

        # First assignment succeeds
        AllocationService.assign_room(
            student=student,
            room=room,
            session='2024/2025',
        )

        # Second assignment for the same session should fail
        room2 = RoomFactory(
            hostel=room.hostel, capacity=4, current_occupancy=0
        )
        with pytest.raises(AlreadyAllocated):
            AllocationService.assign_room(
                student=student,
                room=room2,
                session='2024/2025',
            )

    def test_deallocate_frees_capacity(self):
        """Deallocating an assignment decrements room occupancy."""
        room = RoomFactory(capacity=2, current_occupancy=1)
        assignment = HostelAssignmentFactory(
            room=room,
            status='approved',
        )

        AllocationService.deallocate(assignment)

        room.refresh_from_db()
        assert room.current_occupancy == 0
        assignment.refresh_from_db()
        assert assignment.status == 'checked_out'


class TestRoomChangeService:
    """Tests for RoomChangeService."""

    def test_approve_room_change_swaps_assignments(self):
        """Approving a room change deallocates old room and assigns new one."""
        old_hostel = HostelFactory(hostel_type='male')
        old_room = RoomFactory(
            hostel=old_hostel, capacity=2, current_occupancy=1
        )
        new_room = RoomFactory(
            hostel=old_hostel, capacity=2, current_occupancy=0
        )
        student = StudentFactory(gender='male')
        old_assignment = HostelAssignmentFactory(
            student=student,
            room=old_room,
            session='2024/2025',
            status='approved',
        )

        change_req = RoomChangeService.request_change(
            assignment=old_assignment,
            desired_room=new_room,
            reason='Noisy neighbours',
        )

        new_assignment = RoomChangeService.approve_change(change_req)

        old_room.refresh_from_db()
        new_room.refresh_from_db()

        assert old_room.current_occupancy == 0
        assert new_room.current_occupancy == 1
        assert new_assignment.room_id == new_room.pk

        change_req.refresh_from_db()
        assert change_req.status == 'approved'


class TestFeeService:
    """Tests for FeeService."""

    def test_generate_hostel_fee_creates_fee(self):
        """A hostel fee is created for the assignment's hostel and session."""
        assignment = HostelAssignmentFactory()

        fee = FeeService.generate_hostel_fee(assignment)

        assert fee.hostel_id == assignment.room.hostel_id
        assert fee.session == assignment.session
        assert fee.amount == assignment.room.price_per_bed
