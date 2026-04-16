"""Business logic for the finance app."""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import List, Optional

from django.db.models import QuerySet

from finance.models import (
    FeeStructure,
    InstallmentPayment,
    InstallmentPlan,
    Invoice,
)
from students.models import Student


class InvoiceService:
    """Handles invoice generation, installment creation, and querying."""

    @staticmethod
    def generate_bulk(
        fee_structure_id: int,
        student_ids: Optional[List[int]] = None,
    ) -> dict:
        """Generate invoices for students matching a fee structure.

        If *student_ids* is provided only those students are considered;
        otherwise all students matching the fee structure's programme and
        level are used.

        Returns ``{"created": int, "skipped": int}``.
        """
        fee_structure = FeeStructure.objects.get(id=fee_structure_id)

        if student_ids:
            students = Student.objects.filter(id__in=student_ids)
        else:
            students = Student.objects.filter(
                programme=fee_structure.programme,
                level=fee_structure.level,
            )

        existing_student_ids = set(
            Invoice.objects.filter(
                fee_structure=fee_structure,
                student_id__in=students.values_list('id', flat=True),
            ).values_list('student_id', flat=True)
        )

        due_date = fee_structure.due_date or datetime.date.today()
        new_invoices = [
            Invoice(
                student=student,
                fee_structure=fee_structure,
                amount=fee_structure.amount,
                due_date=due_date,
            )
            for student in students
            if student.id not in existing_student_ids
        ]

        created_count = len(new_invoices)
        if new_invoices:
            Invoice.objects.bulk_create(new_invoices)

            # Auto-create installments when applicable
            if fee_structure.auto_generate:
                # Re-fetch to get IDs (bulk_create on SQLite may not set PKs)
                created_invoices = Invoice.objects.filter(
                    fee_structure=fee_structure,
                    student_id__in=[inv.student_id for inv in new_invoices],
                )
                plans = list(
                    InstallmentPlan.objects.filter(
                        fee_structure=fee_structure, is_active=True,
                    )
                )
                for invoice in created_invoices:
                    for plan in plans:
                        InvoiceService.create_installments(
                            plan=plan, invoice=invoice,
                        )

        skipped = len(existing_student_ids & {s.id for s in students})
        return {'created': created_count, 'skipped': skipped}

    @staticmethod
    def generate_for_student(
        student: Student,
        session: str,
    ) -> List[Invoice]:
        """Generate invoices for a single student for a given session.

        Finds all auto-generate fee structures matching the student's
        programme, level, and session. Skips any fee structure for which an
        invoice already exists.

        Returns the list of newly created Invoice objects.
        """
        fee_structures = FeeStructure.objects.filter(
            programme=student.programme,
            level=student.level,
            session=session,
            auto_generate=True,
        )

        created_invoices: list[Invoice] = []
        for fs in fee_structures:
            invoice, created = Invoice.objects.get_or_create(
                student=student,
                fee_structure=fs,
                defaults={
                    'amount': fs.amount,
                    'due_date': fs.due_date or datetime.date.today(),
                },
            )
            if created:
                created_invoices.append(invoice)
                # Auto-create installments
                plans = InstallmentPlan.objects.filter(
                    fee_structure=fs, is_active=True
                )
                for plan in plans:
                    InvoiceService.create_installments(plan=plan, invoice=invoice)

        return created_invoices

    @staticmethod
    def create_installments(
        plan: InstallmentPlan,
        invoice: Invoice,
    ) -> List[InstallmentPayment]:
        """Create installment payment records for an invoice.

        Divides the invoice amount evenly across the plan's installments
        and assigns due dates from the plan's due_dates list (falling back
        to the invoice's due_date).
        """
        n = plan.number_of_installments
        amount_per = Decimal(str(invoice.amount)) / n

        payments = []
        for i in range(1, n + 1):
            if i - 1 < len(plan.due_dates):
                due = plan.due_dates[i - 1]
            else:
                due = invoice.due_date
            payments.append(
                InstallmentPayment(
                    installment_plan=plan,
                    invoice=invoice,
                    installment_number=i,
                    amount=amount_per,
                    due_date=due,
                )
            )

        return InstallmentPayment.objects.bulk_create(payments, ignore_conflicts=True)

    @staticmethod
    def list_overdue(as_of: Optional[datetime.date] = None) -> QuerySet[Invoice]:
        """Return invoices that are overdue as of the given date."""
        if as_of is None:
            as_of = datetime.date.today()
        return Invoice.objects.filter(
            due_date__lt=as_of,
            status__in=['pending', 'partially_paid'],
        )

    @staticmethod
    def get_visible_to(user) -> QuerySet[Invoice]:
        """Return the queryset of invoices visible to the given user.

        Students see only their own invoices; admins/staff see all.
        """
        base_qs = Invoice.objects.select_related(
            'student__user',
            'fee_structure__fee_type',
            'fee_structure__programme',
        )
        if user.user_type == 'student':
            try:
                student = user.student_profile
                return base_qs.filter(student=student)
            except Student.DoesNotExist:
                return Invoice.objects.none()
        return base_qs.all()
