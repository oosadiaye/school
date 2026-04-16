from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HostelViewSet, RoomViewSet, HostelAssignmentViewSet, HostelFeeViewSet

router = DefaultRouter()
router.register(r'', HostelViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'assignments', HostelAssignmentViewSet)
router.register(r'fees', HostelFeeViewSet)

urlpatterns = [path('', include(router.urls))]
