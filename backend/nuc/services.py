"""Business logic for the NUC app."""
from __future__ import annotations

from datetime import date, timedelta

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from nuc.models import (
    Accreditation,
    ComplianceChecklist,
    ComplianceItem,
    GraduationList,
    NUCReport,
)
from students.models import Programme


class AccreditationService:
    """Handles programme accreditation records."""

    @staticmethod
    @transaction.atomic
    def record_accreditation(
        programme: Programme,
        status: str,
        valid_until: date | None = None,
        *,
        by=None,
    ) -> Accreditation:
        """Create an accreditation entry for a programme.

        Args:
            programme: the programme being accredited.
            status: one of Accreditation.STATUS_CHOICES values.
            valid_until: expiry date; stored as expiry_date.
            by: user performing the action (for audit trail).
        """
        return Accreditation.objects.create(
            programme=programme,
            accreditation_status=status,
            accreditation_date=date.today(),
            expiry_date=valid_until,
        )

    @staticmethod
    def list_expiring(within_days: int = 90) -> QuerySet[Accreditation]:
        """Return accreditations expiring within the given window.

        Useful for Phase 3 Celery alert task.
        """
        today = date.today()
        cutoff = today + timedelta(days=within_days)
        return Accreditation.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=cutoff,
        ).select_related('programme')


class ComplianceService:
    """Handles compliance checklists and items."""

    @staticmethod
    @transaction.atomic
    def create_checklist(
        name: str,
        session: str,
        *,
        by=None,
    ) -> ComplianceChecklist:
        """Create a new compliance checklist.

        Args:
            name: checklist title.
            session: academic session string.
            by: user performing the action (for audit trail).
        """
        return ComplianceChecklist.objects.create(
            name=name,
            description=f"Compliance checklist for session {session}",
        )

    @staticmethod
    @transaction.atomic
    def update_item(
        item: ComplianceItem,
        is_completed: bool,
        evidence: str = '',
        *,
        by=None,
    ) -> ComplianceItem:
        """Update a compliance item's completion status.

        Args:
            item: the ComplianceItem to update.
            is_completed: whether the item is now complete.
            evidence: notes or evidence for completion.
            by: user performing the action (for audit trail).

        Returns:
            A new ComplianceItem instance reflecting the saved state.
        """
        item.is_completed = is_completed
        item.notes = evidence
        if is_completed:
            item.completed_date = date.today()
        else:
            item.completed_date = None
        item.save()
        item.refresh_from_db()
        return item

    @staticmethod
    def completion_percentage(checklist: ComplianceChecklist) -> float:
        """Calculate completion percentage for a checklist.

        Returns 0.0 when the checklist has no items.
        """
        total = checklist.items.count()
        if total == 0:
            return 0.0
        completed = checklist.items.filter(is_completed=True).count()
        return (completed / total) * 100.0


class NUCReportService:
    """Handles NUC reports and graduation lists."""

    @staticmethod
    @transaction.atomic
    def create_report(
        report_type: str,
        session: str,
        *,
        by=None,
    ) -> NUCReport:
        """Create a new NUC report.

        Args:
            report_type: one of NUCReport.REPORT_TYPES values.
            session: academic session string.
            by: user performing the action (for audit trail).
        """
        type_display = dict(NUCReport.REPORT_TYPES).get(report_type, report_type)
        return NUCReport.objects.create(
            title=f"{type_display} - {session}",
            report_type=report_type,
            session=session,
            status='draft',
        )

    @staticmethod
    def graduation_list(
        programme: Programme,
        session: str,
    ) -> QuerySet[GraduationList]:
        """Return graduation lists for a programme and session."""
        return GraduationList.objects.filter(
            programme=programme,
            session=session,
        ).select_related('programme')
