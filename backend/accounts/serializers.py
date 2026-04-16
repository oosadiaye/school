from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import User

PHONE_VALIDATOR = RegexValidator(
    r'^\+?[0-9]{10,15}$',
    'Invalid phone number format. Expected 10-15 digits, optionally prefixed with +.',
)


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        required=False, allow_blank=True,
        validators=[PHONE_VALIDATOR],
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'user_type', 'phone', 'address', 'photo', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    phone = serializers.CharField(
        required=False, allow_blank=True,
        validators=[PHONE_VALIDATOR],
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'user_type', 'phone', 'address']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Validates login request fields. Authentication logic lives in AuthService."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match'})
        return data
