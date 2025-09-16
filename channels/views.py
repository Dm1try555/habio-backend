from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Channel
from .serializers import ChannelSerializer
from rest_framework import permissions
from django.utils import timezone
from datetime import datetime, time
import pytz


class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    @action(detail=False, methods=['get'])
    def widget_config(self, request):
        """Возвращает конфигурацию виджета для фронтенда"""
        project_id = request.query_params.get("project")
        device = request.query_params.get("device", "desktop")
        
        if not project_id:
            return Response({"error": "Project ID is required"}, status=400)
        
        # Получаем каналы для проекта
        channels = Channel.objects.filter(project_id=project_id).order_by('priority', 'id')
        
        # Определяем онлайн статус (простая логика - рабочие часы)
        now = timezone.now()
        current_time = now.time()
        current_weekday = now.weekday()  # 0 = Monday, 6 = Sunday
        
        # Простая логика: рабочие дни с 9:00 до 18:00
        is_online = (
            current_weekday < 5 and  # Понедельник-Пятница
            time(9, 0) <= current_time <= time(18, 0)
        )
        
        next_available = "09:00" if not is_online else None
        
        # Формируем ответ в формате, ожидаемом фронтендом
        response_data = {
            "channels": [
                {
                    "id": channel.id,
                    "type": channel.type,
                    "label": channel.label,
                    "link": channel.link,
                    "phone_number": channel.phone_number,
                    "priority": channel.priority,
                    "show_in_top": channel.show_in_top,
                    "icon": channel.icon,
                    "description": channel.description
                }
                for channel in channels
            ],
            "is_online": is_online,
            "next_available": next_available
        }
        
        return Response(response_data)
