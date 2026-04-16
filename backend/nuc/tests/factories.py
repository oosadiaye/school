"""Factory Boy factories for NUC models."""
from datetime import date, timedelta

import factory
from nuc.models import (
    Accreditation,
    ComplianceChecklist,
    ComplianceItem,
    GraduationList,
    NUCReport,
)
from students.tests.factories import ProgrammeFactory


class AccreditationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Accreditation

    programme = factory.SubFactory(ProgrammeFactory)
    accreditation_status = 'accredited'
    accreditation_date = factory.LazyFunction(date.today)
    expiry_date = factory.LazyFunction(lambda: date.today() + timedelta(days=365))
    nuc_ref_number = factory.Sequence(lambda n: f"NUC-REF-{n:04d}")
    remarks = ''


class NUCReportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NUCReport

    title = factory.Sequence(lambda n: f"NUC Report {n}")
    report_type = 'statistical'
    session = '2024/2025'
    status = 'draft'


class ComplianceChecklistFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceChecklist

    name = factory.Sequence(lambda n: f"Checklist {n}")
    description = 'A compliance checklist.'
    is_active = True


class ComplianceItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceItem

    checklist = factory.SubFactory(ComplianceChecklistFactory)
    name = factory.Sequence(lambda n: f"Item {n}")
    description = 'A compliance item.'
    is_completed = False


class GraduationListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GraduationList

    session = '2024/2025'
    programme = factory.SubFactory(ProgrammeFactory)
    total_graduands = 100
    first_class = 10
    second_class_upper = 30
    second_class_lower = 35
    third_class = 15
    pass_class = 10
    nuc_verified = False
