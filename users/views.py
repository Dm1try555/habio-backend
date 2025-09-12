from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth.hashers import make_password, check_password
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView

from .models import User
from .serializers import UserSerializer, LoginSerializer, RegisterSerializer, ProfileUpdateSerializer, LogoutSerializer, MeSerializer


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@extend_schema(request=LoginSerializer, responses={200: None})
class LoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        # Allow non-unique emails gracefully: prefer superuser, then newest
        user = (
            User.objects
            .filter(email__iexact=email)
            .order_by('-is_superuser', '-date_joined', '-id')
            .first()
        )
        if not user:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
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
        if User.objects.filter(username=data['username']).exists():
            return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            return Response({'detail': 'email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            role=data['role'],
            password=make_password(data['password']),
        )
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LogoutView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LogoutSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data['refresh']

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # делаем отзыв токена
        except TokenError as e:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)
        


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(request=ProfileUpdateSerializer, responses={200: UserSerializer})
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


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


# ===== Split admin/client auth endpoints =====

@extend_schema(request=LoginSerializer, responses={200: None})
class AdminLoginView(LoginView):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Optionally enforce role match if provided
        role = request.data.get('role')
        if not isinstance(response.data, dict) or 'user' not in response.data:
            return response

        user_id = response.data['user'].get('id')
        user_obj = None
        if user_id:
            try:
                user_obj = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user_obj = None

        if role and user_obj:
            # Allow superuser regardless of role
            if user_obj.is_superuser:
                # reflect chosen role in response for UI routing
                try:
                    response.data['user']['role'] = role
                except Exception:
                    pass
                return response
            # Enforce declared role for non-superusers
            if response.data['user'].get('role') != role:
                return Response({'detail': 'Role mismatch'}, status=status.HTTP_403_FORBIDDEN)
        return response


@extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
class AdminRegisterView(RegisterView):
    pass


@extend_schema(request=LoginSerializer, responses={200: None})
class ClientLoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        # Only allow 'viewer' role for client login
        if user.role != 'viewer':
            return Response({'detail': 'Access denied for this role'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_200_OK)


@extend_schema(request=RegisterSerializer, responses={201: None})
class ClientRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if User.objects.filter(username=data['username']).exists():
            return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            return Response({'detail': 'email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user with 'viewer' role (client)
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            role='viewer',
            password=make_password(data['password']),
        )
        
        # Generate JWT tokens for client
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
