from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FeeTypeViewSet, FeeStructureViewSet, InvoiceViewSet,
    PaymentViewSet, ScholarshipViewSet, StudentScholarshipViewSet,
    InstallmentPlanViewSet, FeeWaiverViewSet, FinanceReportViewSet
)

router = DefaultRouter()
router.register(r'fee-types', FeeTypeViewSet, basename='fee-types')
router.register(r'fee-structures', FeeStructureViewSet, basename='fee-structures')
router.register(r'invoices', InvoiceViewSet, basename='invoices')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'scholarships', ScholarshipViewSet, basename='scholarships')
router.register(r'student-scholarships', StudentScholarshipViewSet, basename='student-scholarships')
router.register(r'installment-plans', InstallmentPlanViewSet, basename='installment-plans')
router.register(r'fee-waivers', FeeWaiverViewSet, basename='fee-waivers')
router.register(r'reports', FinanceReportViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
]
