from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    # Legacy views for backward compatibility
    LoginView,
    RegisterView,
    LogoutView,
    MeView,
    ProfileView,
    ProfileDeleteView,
    RefreshTokenView,
    PlanUpdateView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # ===== ViewSet URLs =====
    path('', include(router.urls)),
    
    # ===== Legacy Auth URLs (for backward compatibility) =====
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('auth/profile/', ProfileView.as_view(), name='profile-update'),
    path('auth/profile/delete/', ProfileDeleteView.as_view(), name='profile-delete'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('auth/plan/', PlanUpdateView.as_view(), name='plan-update'),
]
