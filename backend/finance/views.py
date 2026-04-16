from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import models, transaction
from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
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
from .payment_gateway import PaymentGateway, generate_payment_link
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
        """Create installment plan for a fee structure"""
        fee_structure = self.get_object()
        data = request.data
        
        due_dates = data.get('due_dates', [])
        if not due_dates:
            num_installments = int(data.get('number_of_installments', 2))
            amount = float(fee_structure.amount) / num_installments
            base_date = fee_structure.due_date or datetime.now().date()
            due_dates = [(base_date + timedelta(days=30*i)).isoformat() for i in range(1, num_installments+1)]
        
        plan = InstallmentPlan.objects.create(
            name=data.get('name', f"{fee_structure.fee_type.name} Plan"),
            fee_structure=fee_structure,
            number_of_installments=int(data.get('number_of_installments', 2)),
            due_dates=due_dates,
            penalty_percentage=data.get('penalty_percentage', 0)
        )
        return Response(InstallmentPlanSerializer(plan).data, status=201)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('student__user', 'fee_structure__fee_type', 'fee_structure__programme').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'fee_structure']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            try:
                student = user.student_profile
                return Invoice.objects.select_related(
                    'student__user', 'fee_structure__fee_type', 'fee_structure__programme'
                ).filter(student=student)
            except Student.DoesNotExist:
                return Invoice.objects.none()
        return super().get_queryset()

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def generate_invoices(self, request):
        """Generate invoices for students"""
        fee_structure_id = request.data.get('fee_structure_id')
        student_ids = request.data.get('student_ids', [])

        if not fee_structure_id:
            return Response({'error': 'fee_structure_id is required'}, status=400)

        try:
            fee_structure = FeeStructure.objects.get(id=fee_structure_id)
        except FeeStructure.DoesNotExist:
            return Response({'error': 'Fee structure not found'}, status=404)

        if student_ids:
            students = Student.objects.filter(id__in=student_ids)
        else:
            students = Student.objects.filter(programme=fee_structure.programme, level=fee_structure.level)

        existing_invoices = set(
            Invoice.objects.filter(
                fee_structure=fee_structure,
                student_id__in=students.values_list('id', flat=True)
            ).values_list('student_id', flat=True)
        )

        due_date = fee_structure.due_date or datetime.now().date()
        new_invoices = [
            Invoice(
                student=student,
                fee_structure=fee_structure,
                amount=fee_structure.amount,
                due_date=due_date
            )
            for student in students
            if student.id not in existing_invoices
        ]

        created_invoices = Invoice.objects.bulk_create(new_invoices, ignore_conflicts=True)

        if fee_structure.auto_generate and created_invoices:
            self.create_installments_bulk(created_invoices, fee_structure)

        return Response({
            'message': f'{len(created_invoices)} invoices generated',
            'count': len(created_invoices)
        })

    def create_installments_bulk(self, invoices, fee_structure):
        """Create installment payments for invoices in bulk"""
        plans = list(InstallmentPlan.objects.filter(fee_structure=fee_structure, is_active=True))
        if not plans:
            return

        new_payments = []
        for invoice in invoices:
            for plan in plans:
                amount_per_installment = float(invoice.amount) / plan.number_of_installments
                for i in range(1, plan.number_of_installments + 1):
                    due_date = plan.due_dates[i-1] if i-1 < len(plan.due_dates) else invoice.due_date
                    new_payments.append(InstallmentPayment(
                        installment_plan=plan,
                        invoice=invoice,
                        installment_number=i,
                        amount=amount_per_installment,
                        due_date=due_date
                    ))

        InstallmentPayment.objects.bulk_create(new_payments, ignore_conflicts=True)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def generate_for_student(self, request):
        """Generate invoice for a newly registered student"""
        student_id = request.data.get('student_id')
        session = request.data.get('session')
        
        if not student_id:
            return Response({'error': 'student_id is required'}, status=400)

        try:
            student = Student.objects.select_related('programme').get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)

        fee_structures = FeeStructure.objects.filter(
            programme=student.programme,
            level=student.level,
            session=session or student.admission_year,
            auto_generate=True
        )

        created_invoices = []
        for fs in fee_structures:
            invoice, created = Invoice.objects.get_or_create(
                student=student,
                fee_structure=fs,
                defaults={'amount': fs.amount, 'due_date': fs.due_date or datetime.now().date()}
            )
            if created:
                created_invoices.append(invoice)
                self.create_installments_bulk([invoice], fs)

        return Response({
            'message': f'{len(created_invoices)} invoices generated for student',
            'count': len(created_invoices)
        })

    @action(detail=True, methods=['post'])
    def generate_payment_link(self, request, pk=None):
        """Generate payment link for an invoice"""
        invoice = self.get_object()
        provider = request.data.get('provider', 'paystack')
        
        valid_providers = ['paystack', 'flutterwave', 'stripe']
        if provider not in valid_providers:
            return Response(
                {'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'},
                status=400
            )
        
        result = generate_payment_link(invoice, provider)
        return Response(result)

    @action(detail=False, methods=['get'])
    def my_invoices(self, request):
        try:
            student = request.user.student_profile
            invoices = Invoice.objects.select_related(
                'student__user', 'fee_structure__fee_type', 'fee_structure__programme'
            ).filter(student=student)
            invoices = self.paginate_queryset(invoices)
            serializer = self.get_serializer(invoices, many=True)
            return self.get_paginated_response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=404)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def overdue(self, request):
        """Get overdue invoices"""
        today = datetime.now().date()
        overdue = Invoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partially_paid']
        ).select_related('student__user', 'fee_structure__fee_type')
        overdue = self.paginate_queryset(overdue)
        serializer = self.get_serializer(overdue, many=True)
        return self.get_paginated_response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('invoice', 'student__user', 'invoice__fee_structure').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'payment_method']
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            try:
                student = user.student_profile
                return Payment.objects.select_related(
                    'invoice', 'student__user', 'invoice__fee_structure'
                ).filter(student=student)
            except Student.DoesNotExist:
                return Payment.objects.none()
        return super().get_queryset()

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save(
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            status='completed'
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
        invoice_id = request.data.get('invoice_id')
        amount = request.data.get('amount')
        payment_method = request.data.get('payment_method', 'online')
        provider = request.data.get('provider', 'paystack')

        if not invoice_id or not amount:
            return Response({'error': 'invoice_id and amount are required'}, status=400)

        valid_providers = ['paystack', 'flutterwave', 'stripe']
        if provider not in valid_providers:
            return Response(
                {'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'},
                status=400
            )

        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'error': 'Invoice not found'}, status=404)

        payment = Payment.objects.create(
            invoice=invoice,
            student=invoice.student,
            amount=amount,
            payment_method=payment_method,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            status='pending'
        )

        result = generate_payment_link(invoice, provider)
        if result.get('success'):
            payment.reference = result.get('reference')
            payment.save()
            return Response({
                'payment_id': payment.id,
                'transaction_id': payment.transaction_id,
                'authorization_url': result.get('authorization_url'),
                'amount': str(payment.amount),
                'status': 'pending'
            })
        
        payment.status = 'failed'
        payment.save()
        return Response({'error': result.get('message', 'Payment initialization failed')}, status=400)

    @action(detail=False, methods=['post'])
    def verify_payment(self, request):
        reference = request.data.get('reference')
        provider = request.data.get('provider', 'paystack')
        
        if not reference:
            return Response({'error': 'reference is required'}, status=400)

        valid_providers = ['paystack', 'flutterwave', 'stripe']
        if provider not in valid_providers:
            return Response(
                {'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'},
                status=400
            )

        gateway = PaymentGateway(provider)
        result = gateway.verify_transaction(reference)
        
        if result.get('verified'):
            try:
                with transaction.atomic():
                    payment = Payment.objects.select_for_update().get(reference=reference)
                    if payment.status != 'completed':
                        payment.status = 'completed'
                        payment.save()
                        
                        invoice = payment.invoice
                        invoice.amount_paid += payment.amount
                        if invoice.amount_paid >= invoice.amount:
                            invoice.status = 'paid'
                        elif invoice.amount_paid > 0:
                            invoice.status = 'partially_paid'
                        invoice.save()
                        
                        InstallmentPayment.objects.filter(
                            invoice=invoice,
                            is_paid=False,
                            installment_number=1
                        ).update(
                            is_paid=True,
                            paid_date=datetime.now().date()
                        )
                    
                return Response({'status': 'verified', 'payment': PaymentSerializer(payment).data})
            except Payment.DoesNotExist:
                return Response({'error': 'Payment not found'}, status=404)
        
        return Response({'status': 'failed', 'message': result.get('message')}, status=400)

    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        try:
            student = request.user.student_profile
            payments = Payment.objects.select_related(
                'invoice', 'student__user', 'invoice__fee_structure'
            ).filter(student=student)
            payments = self.paginate_queryset(payments)
            serializer = self.get_serializer(payments, many=True)
            return self.get_paginated_response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student profile not found'}, status=404)


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPlan.objects.select_related('fee_structure').all()
    serializer_class = InstallmentPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['get'])
    def installments(self, request, pk=None):
        plan = self.get_object()
        installments = plan.payments.all()
        return Response(InstallmentPaymentSerializer(installments, many=True).data)


class FeeWaiverViewSet(viewsets.ModelViewSet):
    queryset = FeeWaiver.objects.select_related('student__user', 'invoice', 'approved_by').all()
    serializer_class = FeeWaiverSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'is_approved']
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a fee waiver"""
        waiver = self.get_object()
        if waiver.is_approved:
            return Response({'message': 'Waiver already approved'}, status=400)
        
        waiver.is_approved = True
        waiver.approved_by = request.user
        waiver.approved_at = datetime.now()
        waiver.save()

        if waiver.waiver_type == 'full':
            waiver.invoice.balance = 0
            waiver.invoice.status = 'waived'
        elif waiver.waiver_type == 'partial':
            waiver.invoice.balance = max(0, waiver.invoice.balance - waiver.amount)
        elif waiver.waiver_type == 'percentage':
            reduction = waiver.invoice.amount * (waiver.percentage / 100)
            waiver.invoice.balance = max(0, waiver.invoice.balance - reduction)
        
        waiver.invoice.save()
        return Response(FeeWaiverSerializer(waiver).data)


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
        total_collected = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        total_pending = Invoice.objects.filter(status__in=['pending', 'partially_paid']).aggregate(Sum('balance'))['balance__sum'] or 0
        total_invoices = Invoice.objects.count()
        paid_invoices = Invoice.objects.filter(status='paid').count()

        return Response({
            'total_collected': float(total_collected),
            'total_pending': float(total_pending),
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'collection_rate': round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 2)
        })


class FinanceReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Comprehensive finance summary"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        this_month = Payment.objects.filter(
            payment_date__gte=month_start,
            status='completed'
        ).aggregate(
            total=Sum('amount'),
            count=Count('id')
        )
        
        total_collected = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        invoice_stats = Invoice.objects.aggregate(
            total_count=Count('id'),
            paid_count=Count('id', filter=models.Q(status='paid')),
            pending_sum=Sum('balance', filter=models.Q(status__in=['pending', 'partially_paid']))
        )
        
        overdue_invoices = Invoice.objects.filter(
            due_date__lt=today,
            status__in=['pending', 'partially_paid']
        ).count()

        total_invoices = invoice_stats['total_count']
        paid_invoices = invoice_stats['paid_count']
        
        return Response({
            'total_collected': float(total_collected),
            'total_pending': float(invoice_stats['pending_sum'] or 0),
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'collection_rate': round((paid_invoices / total_invoices * 100) if total_invoices > 0 else 0, 2),
            'this_month': {
                'collected': float(this_month['total'] or 0),
                'transactions': this_month['count'] or 0
            }
        })

    @action(detail=False, methods=['get'])
    def by_programme(self, request):
        """Finance breakdown by programme"""
        from students.models import Programme
        
        programme_stats = Invoice.objects.filter(
            fee_structure__programme__isnull=False
        ).values(
            'fee_structure__programme__name'
        ).annotate(
            total_invoices=Count('id'),
            collected=Sum('amount_paid'),
            pending=Sum('balance')
        )
        
        return Response([{
            'programme': stat['fee_structure__programme__name'],
            'total_invoices': stat['total_invoices'],
            'collected': float(stat['collected'] or 0),
            'pending': float(stat['pending'] or 0)
        } for stat in programme_stats])

    @action(detail=False, methods=['get'])
    def by_level(self, request):
        """Finance breakdown by level"""
        level_stats = Invoice.objects.filter(
            fee_structure__level__isnull=False
        ).values(
            'fee_structure__level'
        ).annotate(
            total_invoices=Count('id'),
            collected=Sum('amount_paid'),
            pending=Sum('balance')
        )
        
        return Response([{
            'level': stat['fee_structure__level'],
            'total_invoices': stat['total_invoices'],
            'collected': float(stat['collected'] or 0),
            'pending': float(stat['pending'] or 0)
        } for stat in level_stats])

    @action(detail=False, methods=['get'])
    def payment_trends(self, request):
        """Payment trends over time"""
        days = int(request.query_params.get('days', 30))
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        
        payments = Payment.objects.filter(
            payment_date__gte=start_date,
            status='completed'
        ).extra(
            select={'day': "DATE(payment_date)"}
        ).values('day').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('day')
        
        return Response([{
            'date': p['day'],
            'amount': float(p['total']),
            'count': p['count']
        } for p in payments])

    @action(detail=False, methods=['get'])
    def waivers_report(self, request):
        """Fee waivers report"""
        total_waived = FeeWaiver.objects.filter(is_approved=True).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_waivers': FeeWaiver.objects.filter(is_approved=True).count(),
            'total_amount_waived': float(total_waivered),
            'pending_waivers': FeeWaiver.objects.filter(is_approved=False).count()
        })
