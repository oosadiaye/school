from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from students.models import Student
from .models import (
    FeeType, FeeStructure, Invoice, Payment, Scholarship, StudentScholarship,
    InstallmentPlan, InstallmentPayment, FeeWaiver, PaymentReminder
)
from .serializers import (
    FeeTypeSerializer, FeeStructureSerializer, InvoiceSerializer,
    PaymentSerializer, ScholarshipSerializer, StudentScholarshipSerializer,
    InstallmentPlanSerializer, InstallmentPaymentSerializer, FeeWaiverSerializer
)
from .payment_gateway import generate_payment_link
from .services import (
    FeeWaiverService,
    FinanceReportService,
    InvoiceService,
    PaymentService,
)
import uuid


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type == 'admin'


class FeeTypeViewSet(viewsets.ModelViewSet):
    queryset = FeeType.objects.all()
    serializer_class = FeeTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related('programme', 'fee_type').all()
    serializer_class = FeeStructureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['programme', 'level', 'session', 'fee_type']
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post'])
    def create_installment_plan(self, request, pk=None):
        """Create installment plan for a fee structure."""
        from datetime import datetime, timedelta
        fs = self.get_object()
        data = request.data
        due_dates = data.get('due_dates', [])
        num = int(data.get('number_of_installments', 2))
        if not due_dates:
            base = fs.due_date or datetime.now().date()
            due_dates = [(base + timedelta(days=30 * i)).isoformat() for i in range(1, num + 1)]
        plan = InstallmentPlan.objects.create(
            name=data.get('name', f"{fs.fee_type.name} Plan"),
            fee_structure=fs, number_of_installments=num,
            due_dates=due_dates, penalty_percentage=data.get('penalty_percentage', 0),
        )
        return Response(InstallmentPlanSerializer(plan).data, status=201)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('student__user', 'fee_structure__fee_type', 'fee_structure__programme').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'fee_structure']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return InvoiceService.get_visible_to(self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def generate_invoices(self, request):
        """Generate invoices for students."""
        fee_structure_id = request.data.get('fee_structure_id')
        if not fee_structure_id:
            return Response({'error': 'fee_structure_id is required'}, status=400)
        try:
            FeeStructure.objects.get(id=fee_structure_id)
        except FeeStructure.DoesNotExist:
            return Response({'error': 'Fee structure not found'}, status=404)
        result = InvoiceService.generate_bulk(
            fee_structure_id=fee_structure_id,
            student_ids=request.data.get('student_ids') or None,
        )
        return Response({'message': f'{result["created"]} invoices generated', 'count': result['created']})

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def generate_for_student(self, request):
        """Generate invoices for a newly registered student."""
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'student_id is required'}, status=400)
        try:
            student = Student.objects.select_related('programme').get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)
        session = request.data.get('session') or str(student.admission_year)
        created = InvoiceService.generate_for_student(student=student, session=session)
        return Response({'message': f'{len(created)} invoices generated for student', 'count': len(created)})

    @action(detail=True, methods=['post'])
    def generate_payment_link(self, request, pk=None):
        """Generate payment link for an invoice."""
        invoice = self.get_object()
        provider = request.data.get('provider', 'paystack')
        valid_providers = ['paystack', 'flutterwave', 'stripe']
        if provider not in valid_providers:
            return Response({'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'}, status=400)
        return Response(generate_payment_link(invoice, provider))

    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        """Return the current student's invoices."""
        invoices = InvoiceService.get_visible_to(request.user)
        page = self.paginate_queryset(invoices)
        return self.get_paginated_response(self.get_serializer(page, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def overdue(self, request):
        """Get overdue invoices."""
        page = self.paginate_queryset(InvoiceService.list_overdue())
        return self.get_paginated_response(self.get_serializer(page, many=True).data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('invoice', 'student__user', 'invoice__fee_structure').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'payment_method']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return PaymentService.get_visible_to(self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save(
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            status='completed',
        )
        invoice = payment.invoice
        invoice.amount_paid += payment.amount
        if invoice.amount_paid >= invoice.amount:
            invoice.status = 'paid'
        elif invoice.amount_paid > 0:
            invoice.status = 'partially_paid'
        invoice.save()

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        """Initiate a payment via the gateway."""
        invoice_id = request.data.get('invoice_id')
        if not invoice_id:
            return Response({'error': 'invoice_id is required'}, status=400)
        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)
        provider = request.data.get('provider', 'paystack')
        email = request.user.email or f"{invoice.student.matric_number}@student.edu"
        result = PaymentService.initiate(
            invoice=invoice, provider=provider,
            user_email=email, callback_url=request.data.get('callback_url'),
        )
        return Response(result)

    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        """Verify a payment reference."""
        reference = request.data.get('reference')
        if not reference:
            return Response({'error': 'reference is required'}, status=400)
        payment = PaymentService.verify_and_reconcile(
            reference=reference, provider=request.data.get('provider', 'paystack'),
        )
        return Response({'status': 'verified', 'payment': PaymentSerializer(payment).data})

    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """Return the current user's payments."""
        page = self.paginate_queryset(PaymentService.get_visible_to(request.user))
        return self.get_paginated_response(self.get_serializer(page, many=True).data)


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.select_related('fee_structure').all()
    serializer_class = InstallmentPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'])
    def installments(self, request, pk=None):
        """List installments for a plan."""
        return Response(InstallmentPaymentSerializer(self.get_object().payments.all(), many=True).data)


class FeeWaiverViewSet(viewsets.ModelViewSet):
    queryset = FeeWaiver.objects.select_related('student__user', 'invoice', 'approved_by').all()
    serializer_class = FeeWaiverSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'is_approved']
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a fee waiver."""
        waiver = self.get_object()
        result = FeeWaiverService.approve_waiver(waiver=waiver, approved_by=request.user)
        return Response(FeeWaiverSerializer(result).data)


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.all()
    serializer_class = ScholarshipSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination


class StudentScholarshipViewSet(viewsets.ModelViewSet):
    queryset = StudentScholarship.objects.select_related('student__user', 'scholarship').all()
    serializer_class = StudentScholarshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'session', 'is_active']
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Finance dashboard summary."""
        data = FinanceReportService.summary()
        return Response({
            'total_collected': data['total_collected'],
            'total_pending': data['total_pending'],
            'total_invoices': data['total_invoices'],
            'paid_invoices': data['paid_invoices'],
            'collection_rate': data['collection_rate'],
        })


class FinanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Comprehensive finance summary."""
        return Response(FinanceReportService.summary())

    @action(detail=False, methods=['get'])
    def by_programme(self, request):
        """Finance breakdown by programme."""
        return Response(FinanceReportService.by_programme())

    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Finance breakdown by level."""
        return Response(FinanceReportService.by_level())

    @action(detail=False, methods=['get'])
    def payment_trends(self, request):
        """Payment trends over time."""
        days = int(request.query_params.get('days', 30))
        return Response(FinanceReportService.payment_trends(days=days))

    @action(detail=False, methods=['get'])
    def waivers_report(self, request):
        """Fee waivers report."""
        return Response(FinanceReportService.waivers_report())
