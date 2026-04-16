"""Tests for finance.services — InvoiceService."""
import datetime
from decimal import Decimal

import pytest
from finance.models import InstallmentPayment, Invoice
from finance.services import InvoiceService
from finance.tests.factories import (
    FeeStructureFactory,
    FeeTypeFactory,
    InstallmentPlanFactory,
    InvoiceFactory,
)
from students.tests.factories import StudentFactory
from accounts.tests.factories import UserFactory


# ---------------------------------------------------------------------------
# generate_bulk
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_generate_bulk_creates_invoices_for_matching_students():
    """Matching students without an existing invoice get one created.

    Use session '2025/2026' so the post_save signal (which fires on Student
    creation with admission_year=2024 -> '2024/2025') does not pre-create
    invoices for this fee structure.
    """
    fee_structure = FeeStructureFactory(level='100', session='2025/2026')
    students = StudentFactory.create_batch(
        3,
        programme=fee_structure.programme,
        level='100',
    )
    result = InvoiceService.generate_bulk(
        fee_structure_id=fee_structure.id,
    )
    assert result['created'] == 3
    assert Invoice.objects.filter(fee_structure=fee_structure).count() == 3


@pytest.mark.django_db
def test_generate_bulk_skips_existing_invoices():
    """Students who already have an invoice are not duplicated."""
    fee_structure = FeeStructureFactory(level='100', session='2025/2026')
    student_a = StudentFactory(programme=fee_structure.programme, level='100')
    student_b = StudentFactory(programme=fee_structure.programme, level='100')

    # Pre-create invoice for student_a
    InvoiceFactory(student=student_a, fee_structure=fee_structure)

    result = InvoiceService.generate_bulk(
        fee_structure_id=fee_structure.id,
    )
    assert result['created'] == 1
    assert result['skipped'] == 1
    # Only student_b got a new invoice; student_a still has exactly one
    assert Invoice.objects.filter(
        student=student_a, fee_structure=fee_structure
    ).count() == 1


# ---------------------------------------------------------------------------
# generate_for_student
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_generate_for_student_creates_per_fee_structure():
    """Student with 2 matching auto-generate fee structures gets 2 invoices."""
    student = StudentFactory(level='100')
    fee_type_1 = FeeTypeFactory(name='Tuition')
    fee_type_2 = FeeTypeFactory(name='Lab Fee')
    FeeStructureFactory(
        programme=student.programme,
        level='100',
        session='2024/2025',
        fee_type=fee_type_1,
        auto_generate=True,
    )
    FeeStructureFactory(
        programme=student.programme,
        level='100',
        session='2024/2025',
        fee_type=fee_type_2,
        auto_generate=True,
    )

    invoices = InvoiceService.generate_for_student(
        student=student,
        session='2024/2025',
    )
    assert len(invoices) == 2


# ---------------------------------------------------------------------------
# create_installments
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_create_installments_divides_amount_evenly():
    """Plan with 3 installments on 90000 creates 3 x 30000."""
    fee_structure = FeeStructureFactory(amount=Decimal('90000.00'))
    plan = InstallmentPlanFactory(
        fee_structure=fee_structure,
        number_of_installments=3,
    )
    invoice = InvoiceFactory(
        fee_structure=fee_structure,
        amount=Decimal('90000.00'),
    )
    installments = InvoiceService.create_installments(plan=plan, invoice=invoice)
    assert len(installments) == 3
    assert all(i.amount == Decimal('30000.00') for i in installments)


@pytest.mark.django_db
def test_create_installments_spreads_due_dates():
    """3 installments have due dates from the plan's due_dates list."""
    fee_structure = FeeStructureFactory()
    plan = InstallmentPlanFactory(
        fee_structure=fee_structure,
        number_of_installments=3,
        due_dates=['2025-01-31', '2025-02-28', '2025-03-31'],
    )
    invoice = InvoiceFactory(
        fee_structure=fee_structure,
        amount=Decimal('90000.00'),
    )
    installments = InvoiceService.create_installments(plan=plan, invoice=invoice)
    dates = [str(i.due_date) for i in installments]
    assert dates == ['2025-01-31', '2025-02-28', '2025-03-31']


# ---------------------------------------------------------------------------
# list_overdue
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_list_overdue_excludes_paid():
    """Paid invoices do not appear in the overdue list."""
    past = datetime.date(2024, 1, 1)
    paid_invoice = InvoiceFactory(due_date=past, status='paid')
    # Force paid status since save() recalculates
    Invoice.objects.filter(pk=paid_invoice.pk).update(status='paid')

    pending_invoice = InvoiceFactory(due_date=past, status='pending')
    Invoice.objects.filter(pk=pending_invoice.pk).update(status='pending')

    overdue_qs = InvoiceService.list_overdue(as_of=datetime.date(2025, 1, 1))
    ids = set(overdue_qs.values_list('id', flat=True))
    assert pending_invoice.id in ids
    assert paid_invoice.id not in ids


# ---------------------------------------------------------------------------
# get_visible_to
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_get_visible_to_student_returns_own():
    """Student only sees their own invoices."""
    student = StudentFactory()
    own_invoice = InvoiceFactory(student=student)
    other_invoice = InvoiceFactory()  # belongs to a different student

    qs = InvoiceService.get_visible_to(user=student.user)
    ids = set(qs.values_list('id', flat=True))
    assert own_invoice.id in ids
    assert other_invoice.id not in ids


@pytest.mark.django_db
def test_get_visible_to_admin_returns_all():
    """Admin sees all invoices."""
    admin = UserFactory(user_type='admin')
    InvoiceFactory()
    InvoiceFactory()

    qs = InvoiceService.get_visible_to(user=admin)
    assert qs.count() == 2
