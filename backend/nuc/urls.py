from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccreditationViewSet, NUCReportViewSet, ComplianceChecklistViewSet, ComplianceItemViewSet, GraduationListViewSet

router = DefaultRouter()
router.register(r'accreditations', AccreditationViewSet)
router.register(r'reports', NUCReportViewSet)
router.register(r'checklists', ComplianceChecklistViewSet)
router.register(r'compliance-items', ComplianceItemViewSet)
router.register(r'graduations', GraduationListViewSet)

urlpatterns = [path('', include(router.urls))]
