from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Author, Category, Book, LibraryMember, BookLoan, Reservation
from .serializers import (
    AuthorSerializer, CategorySerializer, BookSerializer,
    LibraryMemberSerializer, BookLoanSerializer, ReservationSerializer
)
from .services import BookService, LoanService, ReservationService


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

    def perform_create(self, serializer):
        BookService.create_book(
            data=serializer.validated_data,
            by=self.request.user,
        )


class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.select_related('user').all()
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

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        qs = LoanService.list_overdue()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.select_related('member__user', 'book').all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['member', 'status', 'book']
    pagination_class = PageNumberPagination
