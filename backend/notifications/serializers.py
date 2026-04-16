from rest_framework import serializers
from .models import Notification, EmailTemplate, SMSTemplate, Announcement

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'read_at', 'link', 'created_at']
        read_only_fields = ['id', 'read_at', 'created_at']

class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'is_active']

class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = ['id', 'name', 'message', 'is_active']

class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'message', 'target_audience', 'is_published', 'publish_date', 'expiry_date', 'created_by', 'created_by_name', 'created_at']
