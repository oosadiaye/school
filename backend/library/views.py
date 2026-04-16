from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from .models import Author, Category, Book, LibraryMember, BookLoan, Reservation
from .serializers import (
    AuthorSerializer, CategorySerializer, BookSerializer, 
    LibraryMemberSerializer, BookLoanSerializer, ReservationSerializer
)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name']
    search_fields = ['name', 'bio']
    pagination_class = PageNumberPagination

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['name']
    pagination_class = PageNumberPagination

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['title', 'isbn', 'author__name']
    filterset_fields = ['category', 'is_active']
    pagination_class = PageNumberPagination

class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.select_related('user', 'programme').all()
    serializer_class = LibraryMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['member_type', 'is_active']
    pagination_class = PageNumberPagination

class BookLoanViewSet(viewsets.ModelViewSet):
    queryset = BookLoan.objects.select_related('member__user', 'book').all()
    serializer_class = BookLoanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['member', 'status', 'book']
    pagination_class = PageNumberPagination

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('member__user', 'book').all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['member', 'status', 'book']
    pagination_class = PageNumberPagination
