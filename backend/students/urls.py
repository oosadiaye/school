from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacultyViewSet, DepartmentViewSet, ProgrammeViewSet, StudentViewSet

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet, basename='faculties')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'programmes', ProgrammeViewSet, basename='programmes')
router.register(r'students', StudentViewSet, basename='students')

urlpatterns = [
    path('', include(router.urls)),
]
