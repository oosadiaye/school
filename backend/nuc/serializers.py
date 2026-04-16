from rest_framework import serializers
from .models import Accreditation, NUCReport, ComplianceChecklist, ComplianceItem, GraduationList

class AccreditationSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    class Meta:
        model = Accreditation
        fields = ['id', 'programme', 'programme_name', 'accreditation_status', 'accreditation_date', 'expiry_date', 'nuc_ref_number', 'visit_date', 'remarks']

class NUCReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = NUCReport
        fields = ['id', 'title', 'report_type', 'session', 'submission_date', 'status', 'report_file', 'remarks']

class ComplianceChecklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceChecklist
        fields = ['id', 'name', 'description', 'is_active']

class ComplianceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceItem
        fields = ['id', 'checklist', 'name', 'description', 'is_completed', 'completed_date', 'notes']

class GraduationListSerializer(serializers.ModelSerializer):
    programme_name = serializers.CharField(source='programme.name', read_only=True)
    class Meta:
        model = GraduationList
        fields = ['id', 'session', 'programme', 'programme_name', 'total_graduands', 'first_class', 'second_class_upper', 'second_class_lower', 'third_class', 'pass_class', 'submission_date', 'nuc_verified']
