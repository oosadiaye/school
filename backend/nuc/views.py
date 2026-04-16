from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Accreditation, NUCReport, ComplianceChecklist, ComplianceItem, GraduationList
from .serializers import (
    AccreditationSerializer,
    NUCReportSerializer,
    ComplianceChecklistSerializer,
    ComplianceItemSerializer,
    GraduationListSerializer,
)
from .services import AccreditationService, ComplianceService, NUCReportService


class AccreditationViewSet(viewsets.ModelViewSet):
    queryset = Accreditation.objects.select_related('programme').all()
    serializer_class = AccreditationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'accreditation_status']
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get'])
    def expiring(self, request):
        days = int(request.query_params.get('within_days', 90))
        qs = AccreditationService.list_expiring(within_days=days)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


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
    filterset_fields = ['is_active']
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'])
    def completion(self, request, pk=None):
        checklist = self.get_object()
        pct = ComplianceService.completion_percentage(checklist)
        return Response({'completion_percentage': pct})


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
