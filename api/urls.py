from rest_framework.routers import DefaultRouter
from .views import ChannelViewSet, LeadViewSet

router = DefaultRouter()
router.register(r'channels', ChannelViewSet)
router.register(r'lead', LeadViewSet)

urlpatterns = router.urls
