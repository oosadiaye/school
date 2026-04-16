"""Factory Boy factories for hostel models."""
from decimal import Decimal

import factory
from accounts.tests.factories import UserFactory
from hostel.models import Hostel, HostelAssignment, HostelFee, Room, RoomChangeRequest
from students.tests.factories import StudentFactory


class HostelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Hostel

    name = factory.Sequence(lambda n: f'Hostel {n}')
    code = factory.Sequence(lambda n: f'HST{n:03d}')
    hostel_type = 'male'
    total_rooms = 50
    capacity = 100
    is_active = True


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    hostel = factory.SubFactory(HostelFactory)
    room_number = factory.Sequence(lambda n: f'R{n:03d}')
    floor = 1
    room_type = 'double'
    capacity = 2
    current_occupancy = 0
    price_per_bed = Decimal('25000.00')
    is_available = True


class HostelAssignmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HostelAssignment

    student = factory.SubFactory(StudentFactory)
    room = factory.SubFactory(RoomFactory)
    session = '2024/2025'
    status = 'approved'
    assigned_by = factory.SubFactory(UserFactory, user_type='admin')


class RoomChangeRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoomChangeRequest

    student = factory.SubFactory(StudentFactory)
    from_room = factory.SubFactory(RoomFactory)
    to_room = factory.SubFactory(RoomFactory)
    reason = 'Need a quieter room.'
    status = 'pending'


class HostelFeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = HostelFee

    hostel = factory.SubFactory(HostelFactory)
    session = '2024/2025'
    amount = Decimal('25000.00')
    due_date = factory.LazyFunction(
        lambda: __import__('datetime').date.today()
        + __import__('datetime').timedelta(days=90)
    )
    is_active = True
