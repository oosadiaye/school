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


# ===========================================================================
# PaymentService
# ===========================================================================

from unittest.mock import patch, MagicMock
from finance.services import PaymentService
from finance.models import Payment
from finance.exceptions import (
    InvalidPaymentProvider,
    PaymentAlreadyVerified,
    PaymentInitiationFailed,
    PaymentVerificationFailed,
)
from finance.tests.factories import PaymentFactory


@pytest.mark.django_db
def test_initiate_creates_pending_payment():
    """Initiate creates a Payment record with status='pending'."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.initialize_transaction.return_value = {
            'success': True,
            'reference': 'REF-123',
            'authorization_url': 'https://pay.example.com/auth',
        }
        result = PaymentService.initiate(
            invoice=invoice,
            provider='paystack',
            user_email='student@test.com',
        )

    payment = Payment.objects.get(id=result['payment_id'])
    assert payment.status == 'pending'
    assert payment.reference == 'REF-123'
    assert result['authorization_url'] == 'https://pay.example.com/auth'


@pytest.mark.django_db
def test_initiate_raises_on_invalid_provider():
    """provider='bitcoin' raises InvalidPaymentProvider."""
    invoice = InvoiceFactory()
    with pytest.raises(InvalidPaymentProvider):
        PaymentService.initiate(
            invoice=invoice,
            provider='bitcoin',
            user_email='student@test.com',
        )


@pytest.mark.django_db
def test_initiate_calls_gateway_and_returns_url():
    """Mock gateway initialize and verify authorization_url in response."""
    invoice = InvoiceFactory(amount=Decimal('50000.00'))

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.initialize_transaction.return_value = {
            'success': True,
            'reference': 'REF-ABC',
            'authorization_url': 'https://checkout.paystack.com/abc',
        }
        result = PaymentService.initiate(
            invoice=invoice,
            provider='paystack',
            user_email='test@example.com',
            callback_url='https://myapp.com/callback',
        )

    assert 'authorization_url' in result
    assert result['authorization_url'] == 'https://checkout.paystack.com/abc'
    instance.initialize_transaction.assert_called_once()


@pytest.mark.django_db
def test_initiate_sets_failed_when_gateway_fails():
    """If gateway returns success=False, payment status is 'failed' and exception raised."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.initialize_transaction.return_value = {
            'success': False,
            'message': 'Network error',
        }
        with pytest.raises(PaymentInitiationFailed):
            PaymentService.initiate(
                invoice=invoice,
                provider='paystack',
                user_email='student@test.com',
            )

    # Payment was created then marked failed
    payment = Payment.objects.filter(invoice=invoice, status='failed').first()
    assert payment is not None


@pytest.mark.django_db
def test_verify_and_reconcile_updates_payment_and_invoice():
    """Successful verification updates payment status and reduces invoice balance."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))
    payment = PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        amount=Decimal('10000.00'),
        status='pending',
        reference='REF-VERIFY',
    )

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.verify_transaction.return_value = {
            'verified': True,
            'amount': 10000.0,
            'reference': 'REF-VERIFY',
        }
        result = PaymentService.verify_and_reconcile(
            reference='REF-VERIFY',
            provider='paystack',
        )

    assert result.status == 'completed'
    invoice.refresh_from_db()
    assert invoice.amount_paid == Decimal('10000.00')
    assert invoice.status == 'paid'


@pytest.mark.django_db
def test_verify_raises_already_verified():
    """Payment with status='completed' raises PaymentAlreadyVerified."""
    invoice = InvoiceFactory()
    PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        status='completed',
        reference='REF-DONE',
    )

    with pytest.raises(PaymentAlreadyVerified):
        PaymentService.verify_and_reconcile(
            reference='REF-DONE',
            provider='paystack',
        )


@pytest.mark.django_db
def test_verify_raises_when_gateway_says_failed():
    """Mock gateway verify failure raises PaymentVerificationFailed."""
    invoice = InvoiceFactory()
    PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        status='pending',
        reference='REF-FAIL',
    )

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.verify_transaction.return_value = {
            'verified': False,
            'message': 'Transaction not found',
        }
        with pytest.raises(PaymentVerificationFailed):
            PaymentService.verify_and_reconcile(
                reference='REF-FAIL',
                provider='paystack',
            )

    payment = Payment.objects.get(reference='REF-FAIL')
    assert payment.status == 'failed'


@pytest.mark.django_db
def test_partial_payment_reduces_balance_without_marking_paid():
    """Invoice.amount=10000, payment.amount=5000 -> partially_paid."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))
    payment = PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        amount=Decimal('5000.00'),
        status='pending',
        reference='REF-PARTIAL',
    )

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.verify_transaction.return_value = {
            'verified': True,
            'amount': 5000.0,
            'reference': 'REF-PARTIAL',
        }
        PaymentService.verify_and_reconcile(
            reference='REF-PARTIAL',
            provider='paystack',
        )

    invoice.refresh_from_db()
    assert invoice.amount_paid == Decimal('5000.00')
    assert invoice.balance == Decimal('5000.00')
    assert invoice.status == 'partially_paid'


@pytest.mark.django_db
def test_full_payment_marks_invoice_paid():
    """Invoice.amount=10000, payment.amount=10000 -> paid."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))
    PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        amount=Decimal('10000.00'),
        status='pending',
        reference='REF-FULL',
    )

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.verify_transaction.return_value = {
            'verified': True,
            'amount': 10000.0,
            'reference': 'REF-FULL',
        }
        PaymentService.verify_and_reconcile(
            reference='REF-FULL',
            provider='paystack',
        )

    invoice.refresh_from_db()
    assert invoice.balance == Decimal('0.00')
    assert invoice.status == 'paid'


@pytest.mark.django_db
def test_verify_is_idempotent():
    """Calling verify twice with same reference: second raises PaymentAlreadyVerified."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))
    PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        amount=Decimal('10000.00'),
        status='pending',
        reference='REF-IDEM',
    )

    with patch('finance.services.PaymentGateway') as MockGW:
        instance = MockGW.return_value
        instance.verify_transaction.return_value = {
            'verified': True,
            'amount': 10000.0,
            'reference': 'REF-IDEM',
        }
        PaymentService.verify_and_reconcile(reference='REF-IDEM', provider='paystack')

    # Second call should raise
    with pytest.raises(PaymentAlreadyVerified):
        PaymentService.verify_and_reconcile(reference='REF-IDEM', provider='paystack')


@pytest.mark.django_db
def test_get_visible_to_student_returns_own_payments():
    """Student sees only own payments."""
    student = StudentFactory()
    own_payment = PaymentFactory(
        invoice=InvoiceFactory(student=student),
        student=student,
    )
    other_payment = PaymentFactory()

    qs = PaymentService.get_visible_to(user=student.user)
    ids = set(qs.values_list('id', flat=True))
    assert own_payment.id in ids
    assert other_payment.id not in ids


@pytest.mark.django_db
def test_get_visible_to_admin_returns_all_payments():
    """Admin sees all payments."""
    admin = UserFactory(user_type='admin')
    PaymentFactory()
    PaymentFactory()

    qs = PaymentService.get_visible_to(user=admin)
    assert qs.count() == 2


# ===========================================================================
# FeeWaiverService
# ===========================================================================

from finance.services import FeeWaiverService
from finance.exceptions import WaiverAlreadyApproved
from finance.tests.factories import FeeWaiverFactory


@pytest.mark.django_db
def test_approve_full_waiver_zeros_invoice_balance():
    """Full waiver sets invoice balance to 0 and status to waived."""
    invoice = InvoiceFactory(amount=Decimal('50000.00'))
    waiver = FeeWaiverFactory(invoice=invoice, waiver_type='full')
    admin = UserFactory(user_type='admin')

    result = FeeWaiverService.approve_waiver(waiver=waiver, approved_by=admin)

    assert result.is_approved is True
    invoice.refresh_from_db()
    assert invoice.balance == Decimal('0.00')
    assert invoice.status == 'waived'


@pytest.mark.django_db
def test_approve_partial_waiver_reduces_balance():
    """Partial waiver reduces invoice balance by waiver.amount."""
    invoice = InvoiceFactory(amount=Decimal('50000.00'))
    waiver = FeeWaiverFactory(
        invoice=invoice,
        waiver_type='partial',
        amount=Decimal('20000.00'),
    )
    admin = UserFactory(user_type='admin')

    FeeWaiverService.approve_waiver(waiver=waiver, approved_by=admin)

    invoice.refresh_from_db()
    assert invoice.balance == Decimal('30000.00')


@pytest.mark.django_db
def test_approve_percentage_waiver_calculates_correctly():
    """Percentage waiver reduces balance by (invoice.amount * percentage / 100)."""
    invoice = InvoiceFactory(amount=Decimal('100000.00'))
    waiver = FeeWaiverFactory(
        invoice=invoice,
        waiver_type='percentage',
        percentage=Decimal('25.00'),
    )
    admin = UserFactory(user_type='admin')

    FeeWaiverService.approve_waiver(waiver=waiver, approved_by=admin)

    invoice.refresh_from_db()
    assert invoice.balance == Decimal('75000.00')


@pytest.mark.django_db
def test_approve_already_approved_raises_conflict():
    """Approving an already-approved waiver raises WaiverAlreadyApproved."""
    invoice = InvoiceFactory(amount=Decimal('50000.00'))
    waiver = FeeWaiverFactory(invoice=invoice, waiver_type='full', is_approved=True)
    admin = UserFactory(user_type='admin')

    with pytest.raises(WaiverAlreadyApproved):
        FeeWaiverService.approve_waiver(waiver=waiver, approved_by=admin)


# ===========================================================================
# FinanceReportService
# ===========================================================================

from finance.services import FinanceReportService


@pytest.mark.django_db
def test_summary_returns_correct_totals():
    """Summary aggregates total collected, pending, and collection rate."""
    invoice = InvoiceFactory(amount=Decimal('10000.00'))
    PaymentFactory(
        invoice=invoice,
        student=invoice.student,
        amount=Decimal('10000.00'),
        status='completed',
    )
    # Reconcile the invoice so it reflects paid status
    invoice.amount_paid = Decimal('10000.00')
    invoice.save()

    result = FinanceReportService.summary()

    assert result['total_collected'] == float(Decimal('10000.00'))
    assert result['total_invoices'] >= 1
    assert 'collection_rate' in result
    assert 'this_month' in result


@pytest.mark.django_db
def test_summary_handles_empty_database():
    """Summary on empty DB returns zeros without crashing."""
    result = FinanceReportService.summary()

    assert result['total_collected'] == 0.0
    assert result['total_invoices'] == 0
    assert result['collection_rate'] == 0
    assert result['this_month']['collected'] == 0.0


@pytest.mark.django_db
def test_payment_trends_returns_list():
    """payment_trends returns a list (possibly empty)."""
    result = FinanceReportService.payment_trends(days=30)

    assert isinstance(result, list)
