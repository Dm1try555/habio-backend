from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserListCreateView,
    UserDetailView,
    LoginView,
    RegisterView,
    LogoutView,
    MeView,
    ProfileView,
    ProfileDeleteView,
    RefreshTokenView,
    AdminLoginView,
    AdminRegisterView,
    ClientLoginView,
    ClientRegisterView,
)

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('auth/login/', LoginView.as_view(), name='users-login'),
    path('auth/register/', RegisterView.as_view(), name='users-register'),
    # Admin-specific
    path('admin/auth/login/', AdminLoginView.as_view(), name='admin-login'),
    path('admin/auth/register/', AdminRegisterView.as_view(), name='admin-register'),
    # Client-specific
    path('client/auth/login/', ClientLoginView.as_view(), name='client-login'),
    path('client/auth/register/', ClientRegisterView.as_view(), name='client-register'),
    path('auth/logout/', LogoutView.as_view(), name='users-logout'),
    path('auth/me/', MeView.as_view(), name='users-me'),
    path('auth/profile/', ProfileView.as_view(), name='users-profile'),
    path('auth/profile/delete/', ProfileDeleteView.as_view(), name='users-profile-delete'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='users-refresh'),
]
