"""Tests for NUC service layer."""
from datetime import date, timedelta

import pytest

from nuc.services import AccreditationService, ComplianceService, NUCReportService
from nuc.tests.factories import (
    AccreditationFactory,
    ComplianceChecklistFactory,
    ComplianceItemFactory,
    GraduationListFactory,
)
from students.tests.factories import ProgrammeFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# AccreditationService
# ---------------------------------------------------------------------------

class TestAccreditationService:

    def test_record_accreditation_creates_entry(self):
        programme = ProgrammeFactory()
        valid_until = date.today() + timedelta(days=365)

        accreditation = AccreditationService.record_accreditation(
            programme=programme,
            status='accredited',
            valid_until=valid_until,
        )

        assert accreditation.pk is not None
        assert accreditation.programme == programme
        assert accreditation.accreditation_status == 'accredited'
        assert accreditation.expiry_date == valid_until
        assert accreditation.accreditation_date == date.today()

    def test_list_expiring_filters_within_window(self):
        programme = ProgrammeFactory()
        # Expiring in 30 days — should be included in 90-day window
        AccreditationFactory(
            programme=programme,
            expiry_date=date.today() + timedelta(days=30),
        )
        # Expiring in 180 days — should NOT be included
        AccreditationFactory(
            programme=programme,
            expiry_date=date.today() + timedelta(days=180),
        )
        # Already expired — should NOT be included
        AccreditationFactory(
            programme=programme,
            expiry_date=date.today() - timedelta(days=10),
        )

        expiring = AccreditationService.list_expiring(within_days=90)

        assert expiring.count() == 1
        assert expiring.first().expiry_date == date.today() + timedelta(days=30)


# ---------------------------------------------------------------------------
# ComplianceService
# ---------------------------------------------------------------------------

class TestComplianceService:

    def test_completion_percentage_100_when_all_complete(self):
        checklist = ComplianceChecklistFactory()
        ComplianceItemFactory(checklist=checklist, is_completed=True)
        ComplianceItemFactory(checklist=checklist, is_completed=True)
        ComplianceItemFactory(checklist=checklist, is_completed=True)

        pct = ComplianceService.completion_percentage(checklist)

        assert pct == 100.0

    def test_completion_percentage_partial(self):
        checklist = ComplianceChecklistFactory()
        ComplianceItemFactory(checklist=checklist, is_completed=True)
        ComplianceItemFactory(checklist=checklist, is_completed=False)
        ComplianceItemFactory(checklist=checklist, is_completed=False)
        ComplianceItemFactory(checklist=checklist, is_completed=False)

        pct = ComplianceService.completion_percentage(checklist)

        assert pct == 25.0

    def test_create_checklist_creates_entry(self):
        checklist = ComplianceService.create_checklist(
            name='BMAS Checklist',
            session='2024/2025',
        )

        assert checklist.pk is not None
        assert checklist.name == 'BMAS Checklist'
        assert '2024/2025' in checklist.description

    def test_update_item_marks_completed(self):
        item = ComplianceItemFactory(is_completed=False)

        updated = ComplianceService.update_item(
            item=item,
            is_completed=True,
            evidence='Submitted documentation.',
        )

        assert updated.is_completed is True
        assert updated.notes == 'Submitted documentation.'
        assert updated.completed_date == date.today()


# ---------------------------------------------------------------------------
# NUCReportService
# ---------------------------------------------------------------------------

class TestNUCReportService:

    def test_create_report_creates_entry(self):
        report = NUCReportService.create_report(
            report_type='statistical',
            session='2024/2025',
        )

        assert report.pk is not None
        assert report.report_type == 'statistical'
        assert report.session == '2024/2025'
        assert report.status == 'draft'

    def test_graduation_list_filters_correctly(self):
        programme = ProgrammeFactory()
        other_programme = ProgrammeFactory()

        GraduationListFactory(programme=programme, session='2024/2025')
        GraduationListFactory(programme=programme, session='2023/2024')
        GraduationListFactory(programme=other_programme, session='2024/2025')

        results = NUCReportService.graduation_list(
            programme=programme,
            session='2024/2025',
        )

        assert results.count() == 1
        assert results.first().programme == programme
        assert results.first().session == '2024/2025'
