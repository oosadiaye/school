"""Factory Boy factories for finance models."""
import datetime
from decimal import Decimal

import factory
from finance.models import (
    FeeStructure,
    FeeType,
    InstallmentPlan,
    InstallmentPayment,
    Invoice,
    Payment,
)
from students.tests.factories import ProgrammeFactory, StudentFactory


class FeeTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeeType

    name = factory.Sequence(lambda n: f'Tuition Fee {n}')
    description = 'Standard tuition fee'
    is_active = True


class FeeStructureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FeeStructure

    programme = factory.SubFactory(ProgrammeFactory)
    fee_type = factory.SubFactory(FeeTypeFactory)
    amount = Decimal('90000.00')
    level = '100'
    session = '2024/2025'
    is_mandatory = True
    due_date = factory.LazyFunction(lambda: datetime.date(2025, 3, 31))
    auto_generate = True


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Invoice

    student = factory.SubFactory(StudentFactory)
    fee_structure = factory.SubFactory(FeeStructureFactory)
    amount = factory.LazyAttribute(lambda o: o.fee_structure.amount)
    due_date = factory.LazyAttribute(
        lambda o: o.fee_structure.due_date or datetime.date(2025, 3, 31)
    )
    status = 'pending'


class InstallmentPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InstallmentPlan

    name = factory.Sequence(lambda n: f'Installment Plan {n}')
    fee_structure = factory.SubFactory(FeeStructureFactory)
    number_of_installments = 3
    due_dates = factory.LazyFunction(lambda: [
        '2025-01-31',
        '2025-02-28',
        '2025-03-31',
    ])
    penalty_percentage = Decimal('0.00')
    is_active = True


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    invoice = factory.SubFactory(InvoiceFactory)
    student = factory.LazyAttribute(lambda o: o.invoice.student)
    amount = Decimal('10000.00')
    payment_method = 'online'
    transaction_id = factory.Sequence(lambda n: f'TXN-TEST{n:08d}')
    status = 'completed'
