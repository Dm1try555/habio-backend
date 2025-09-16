from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API schema and Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('users.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('channels.urls')),
    path('api/', include('schedules.urls')),
    path('api/', include('leads.urls')),
    path('api/', include('chat.urls')),
    path('api/', include('abtests.urls')),
    path('api/', include('widget.urls')),
]
