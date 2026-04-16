from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer,
    ChangePasswordSerializer,
)
from .services import AuthService
from core.exceptions import ValidationFailed

User = get_user_model()


class LoginRateThrottle(UserRateThrottle):
    scope = 'login'


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.login(
            serializer.validated_data['username'],
            serializer.validated_data['password'],
        )
        return Response(result)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            raise ValidationFailed('refresh_token is required')
        result = AuthService.refresh_access_token(refresh_token)
        return Response(result)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filterset_fields = ['user_type', 'is_active', 'is_staff']
    search_fields = ['first_name', 'last_name', 'email', 'username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login', 'refresh']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(
            request.user,
            serializer.validated_data['old_password'],
            serializer.validated_data['new_password'],
        )
        return Response({'message': 'Password changed successfully'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
