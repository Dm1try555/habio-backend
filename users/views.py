from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import make_password, check_password
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate

from .models import User
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer, 
    ProfileUpdateSerializer, LogoutSerializer, MeSerializer, PlanUpdateSerializer
)


# ===== Permissions =====
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser))


# ===== User CRUD =====
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """Аутентификация пользователя"""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        role = request.data.get('role', None)  

        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if role and user.role != role and not user.is_superuser:
            return Response({'detail': 'Role mismatch'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Регистрация нового пользователя"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data['email']).exists():
            return Response({'detail': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        role = data.get('role', 'viewer')
        plan = data.get('plan', 'free')

        user = User.objects.create(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            plan=plan,
            password=make_password(data['password']),
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """Выход из системы"""
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Получение информации о текущем пользователе"""
        serializer = MeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """Обновление профиля текущего пользователя"""
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def delete_profile(self, request):
        """Удаление профиля текущего пользователя"""
        user = request.user
        user.is_active = False
        user.save()
        return Response({"detail": "Profile deleted successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_plan(self, request):
        """Обновление плана пользователя"""
        serializer = PlanUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_plan = serializer.validated_data['plan']

        user = request.user
        user.plan = new_plan
        user.save(update_fields=['plan'])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def refresh_token(self, request):
        """Обновление токена доступа"""
        return TokenRefreshView.as_view()(request)


# ===== Auth (Legacy views for backward compatibility) =====
@extend_schema(request=LoginSerializer, responses={200: None})
class LoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        role = request.data.get('role', None)  

        
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        
        if role and user.role != role and not user.is_superuser:
            return Response({'detail': 'Role mismatch'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


@extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data['email']).exists():
            return Response({'detail': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        
        role = data.get('role', 'viewer')
        plan = data.get('plan', 'free')

        user = User.objects.create(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=role,
            plan=plan,
            password=make_password(data['password']),
        )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


# ===== Logout =====
class LogoutView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)


# ===== Me / Profile =====
class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProfileView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer

    def get_object(self):
        return self.request.user


class ProfileDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


# ===== Plan Update =====
class PlanUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlanUpdateSerializer

    def get_object(self):
        # user updates own plan; admins can update anyone via admin endpoints
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_plan = serializer.validated_data['plan']

        user: User = request.user
        user.plan = new_plan
        user.save(update_fields=['plan'])
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


# ===== Token Refresh =====
class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
