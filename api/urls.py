from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    ProjectConfigViewSet, ChannelViewSet, ScheduleViewSet, 
    LeadViewSet, CallbackRequestViewSet, WidgetAPIView
)

router = DefaultRouter()
router.register(r'projects', ProjectConfigViewSet)
router.register(r'channels', ChannelViewSet)
router.register(r'schedules', ScheduleViewSet)
router.register(r'leads', LeadViewSet)
router.register(r'callbacks', CallbackRequestViewSet)
router.register(r'widget', WidgetAPIView, basename='widget')

urlpatterns = [
    path('', include(router.urls)),
]
