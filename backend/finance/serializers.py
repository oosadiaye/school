from rest_framework import serializers
from django.core.validators import MinValueValidator
from .models import (
    FeeType, FeeStructure, Invoice, Payment, Scholarship, StudentScholarship, PaymentReminder,
    InstallmentPlan, InstallmentPayment, FeeWaiver
)


class FeeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeType
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeeStructureSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    fee_type_name = serializers.CharField(source='fee_type.name', read_only=True)
    
    class Meta:
        model = FeeStructure
        fields = ['id', 'programme', 'programme_name', 'fee_type', 'fee_type_name',
                  'amount', 'level', 'session', 'is_mandatory', 'due_date', 'auto_generate',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstallmentPlanSerializer(serializers.ModelSerializer):
    fee_structure_name = serializers.CharField(source='fee_structure.fee_type.name', read_only=True)
    
    class Meta:
        model = InstallmentPlan
        fields = ['id', 'name', 'fee_structure', 'fee_structure_name', 'number_of_installments',
                  'due_dates', 'penalty_percentage', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = ['id', 'installment_plan', 'invoice', 'installment_number', 'amount',
                  'due_date', 'is_paid', 'paid_date', 'penalty_amount']


class FeeWaiverSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    invoice_details = serializers.SerializerMethodField()
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = FeeWaiver
        fields = ['id', 'student', 'student_name', 'invoice', 'invoice_details', 'waiver_type',
                  'amount', 'percentage', 'reason', 'approved_by', 'approved_by_name',
                  'is_approved', 'created_at', 'approved_at']
        read_only_fields = ['id', 'created_at']

    def get_invoice_details(self, obj):
        return {
            'amount': str(obj.invoice.amount),
            'balance': str(obj.invoice.balance),
            'status': obj.invoice.status
        }

    def validate(self, data):
        amount = data.get('amount')
        percentage = data.get('percentage')
        has_amount = amount is not None and amount > 0
        has_percentage = percentage is not None and percentage > 0
        if has_amount and has_percentage:
            raise serializers.ValidationError(
                'Provide either amount or percentage, not both.'
            )
        if has_amount and amount <= 0:
            raise serializers.ValidationError({'amount': 'Amount must be greater than 0.'})
        if has_percentage and (percentage < 1 or percentage > 100):
            raise serializers.ValidationError({
                'percentage': 'Percentage must be between 1 and 100.'
            })
        return data


class InvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    fee_type_name = serializers.CharField(source='fee_structure.fee_type.name', read_only=True)
    has_installments = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ['id', 'student', 'student_name', 'student_matric', 'fee_structure',
                  'fee_type_name', 'amount', 'amount_paid', 'balance', 'status',
                  'due_date', 'generated_at', 'updated_at', 'has_installments']
        read_only_fields = ['id', 'generated_at', 'updated_at']

    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Invoice amount must be greater than 0.')
        return value
    
    def get_has_installments(self, obj):
        return InstallmentPayment.objects.filter(invoice=obj).exists()


class PaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'invoice', 'student', 'student_name', 'student_matric',
                  'amount', 'payment_method', 'transaction_id', 'reference',
                  'payment_date', 'status', 'channel', 'description', 'created_at']
        read_only_fields = ['id', 'payment_date', 'created_at']

    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError('Payment amount must be greater than 0.')
        return value


class ScholarshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scholarship
        fields = ['id', 'name', 'description', 'amount', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentScholarshipSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_matric = serializers.CharField(source='student.matric_number', read_only=True)
    scholarship_name = serializers.CharField(source='scholarship.name', read_only=True)
    
    class Meta:
        model = StudentScholarship
        fields = ['id', 'student', 'student_name', 'student_matric', 'scholarship',
                  'scholarship_name', 'session', 'start_date', 'end_date', 
                  'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']
