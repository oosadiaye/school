from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, UserCreateSerializer, LoginSerializer, 
    ChangePasswordSerializer
)
from .authentication import generate_token, generate_refresh_token
import jwt
from django.conf import settings

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
        user = serializer.validated_data['user']
        
        access_token = generate_token(user)
        refresh_token = generate_refresh_token(user)
        
        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        token = request.data.get('refresh_token')
        if not token:
            return Response({'error': 'Refresh token required'}, status=400)
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            access_token = generate_token(user)
            return Response({'access_token': access_token})
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=401)


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
        
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
