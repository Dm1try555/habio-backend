from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ABTestViewSet, ABTestVariantViewSet, UserVariantViewSet

router = DefaultRouter()
router.register(r'ab-tests', ABTestViewSet, basename='ab-test')
router.register(r'ab-test-variants', ABTestVariantViewSet, basename='ab-test-variant')
router.register(r'user-variants', UserVariantViewSet, basename='user-variant')

urlpatterns = [
    path('', include(router.urls)),
]
