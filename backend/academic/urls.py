from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AcademicSessionViewSet, SemesterViewSet, CourseViewSet,
    CourseAllocationViewSet, CourseRegistrationViewSet,
    AttendanceViewSet, ResultViewSet, ExamSittingViewSet
)

router = DefaultRouter()
router.register(r'sessions', AcademicSessionViewSet, basename='sessions')
router.register(r'semesters', SemesterViewSet, basename='semesters')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'course-allocations', CourseAllocationViewSet, basename='course-allocations')
router.register(r'course-registrations', CourseRegistrationViewSet, basename='course-registrations')
router.register(r'attendances', AttendanceViewSet, basename='attendances')
router.register(r'results', ResultViewSet, basename='results')
router.register(r'exam-sittings', ExamSittingViewSet, basename='exam-sittings')

urlpatterns = [
    path('', include(router.urls)),
]
