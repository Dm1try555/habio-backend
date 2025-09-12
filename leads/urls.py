from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, CallbackRequestViewSet

router = DefaultRouter()
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'callbacks', CallbackRequestViewSet, basename='callback')

urlpatterns = [
    path('', include(router.urls)),
]
