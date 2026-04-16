from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Accreditation, NUCReport, ComplianceChecklist, ComplianceItem, GraduationList
from .serializers import AccreditationSerializer, NUCReportSerializer, ComplianceChecklistSerializer, ComplianceItemSerializer, GraduationListSerializer

class AccreditationViewSet(viewsets.ModelViewSet):
    queryset = Accreditation.objects.select_related('programme').all()
    serializer_class = AccreditationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'accreditation_status']
    pagination_class = PageNumberPagination

class NUCReportViewSet(viewsets.ModelViewSet):
    queryset = NUCReport.objects.all()
    serializer_class = NUCReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['report_type', 'session', 'status']
    pagination_class = PageNumberPagination

class ComplianceChecklistViewSet(viewsets.ModelViewSet):
    queryset = ComplianceChecklist.objects.all()
    serializer_class = ComplianceChecklistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['session', 'is_completed']
    pagination_class = PageNumberPagination

class ComplianceItemViewSet(viewsets.ModelViewSet):
    queryset = ComplianceItem.objects.all()
    serializer_class = ComplianceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['checklist', 'is_completed']
    pagination_class = PageNumberPagination

class GraduationListViewSet(viewsets.ModelViewSet):
    queryset = GraduationList.objects.select_related('programme').all()
    serializer_class = GraduationListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'session', 'nuc_verified']
    pagination_class = PageNumberPagination
