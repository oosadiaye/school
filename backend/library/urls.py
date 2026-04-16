from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, CategoryViewSet, BookViewSet, LibraryMemberViewSet, BookLoanViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'books', BookViewSet)
router.register(r'members', LibraryMemberViewSet)
router.register(r'loans', BookLoanViewSet)
router.register(r'reservations', ReservationViewSet)

urlpatterns = [path('', include(router.urls))]
