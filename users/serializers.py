from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'plan', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['date_joined']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[('admin','admin'), ('marketing','marketing'), ('viewer','viewer')], default='viewer')


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=[('admin','admin'), ('marketing','marketing'), ('viewer','viewer')], default='viewer')
    plan = serializers.ChoiceField(choices=[('free','free'), ('pro','pro')], default='free')


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'plan', 'first_name', 'last_name', 'is_active', 'date_joined', 'is_staff', 'is_superuser']


class PlanUpdateSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=[('free','free'), ('pro','pro')])