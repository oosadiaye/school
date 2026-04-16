from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Notification, EmailTemplate, SMSTemplate, Announcement
from .serializers import NotificationSerializer, EmailTemplateSerializer, SMSTemplateSerializer, AnnouncementSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.select_related('user').all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['notification_type', 'is_read']
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return Notification.objects.select_related('user').filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})

class EmailTemplateViewSet(viewsets.ModelViewSet):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active']
    pagination_class = PageNumberPagination

class SMSTemplateViewSet(viewsets.ModelViewSet):
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_active']
    pagination_class = PageNumberPagination

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.select_related('created_by').all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['target_audience', 'is_published']
    pagination_class = PageNumberPagination
