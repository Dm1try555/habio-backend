from django.urls import path
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
)

urlpatterns = [
    # ===== Users =====
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # ===== Auth =====
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/profile/', ProfileView.as_view(), name='profile-update'),
    path('auth/profile/delete/', ProfileDeleteView.as_view(), name='profile-delete'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
]
