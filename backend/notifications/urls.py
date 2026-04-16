from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, EmailTemplateViewSet, SMSTemplateViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register(r'', NotificationViewSet)
router.register(r'email-templates', EmailTemplateViewSet)
router.register(r'sms-templates', SMSTemplateViewSet)
router.register(r'announcements', AnnouncementViewSet)

urlpatterns = [path('', include(router.urls))]
