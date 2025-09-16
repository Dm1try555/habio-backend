from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, time
import pytz

from projects.models import Project
from channels.models import Channel
from leads.models import Lead, CallbackRequest
from chat.models import ChatSession, ChatMessage
from leads.serializers import LeadSerializer, CallbackRequestSerializer
from chat.serializers import ChatSessionSerializer, ChatMessageSerializer


class WidgetViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'], url_path='channels/(?P<project_id>[^/.]+)')
    def get_channels(self, request, project_id=None):
        """Получение каналов для виджета"""
        try:
            project = get_object_or_404(Project, id=project_id)
            channels = Channel.objects.filter(project=project, is_active=True).order_by('priority', 'id')
            
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
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_lead/(?P<project_id>[^/.]+)')
    def create_lead(self, request, project_id=None):
        """Создание лида через виджет"""
        try:
            project = get_object_or_404(Project, id=project_id)
            channel_id = request.data.get('channel')
            if channel_id:
                channel = get_object_or_404(Channel, id=channel_id)
            else:
                # Создаем дефолтный канал если не указан
                channel, created = Channel.objects.get_or_create(
                    project=project,
                    type='form',
                    defaults={
                        'label': 'Форма обратной связи',
                        'priority': 1,
                        'is_active': True
                    }
                )
            
            lead = Lead.objects.create(
                project=project,
                channel=channel,
                contact=request.data.get('contact', ''),
                message=request.data.get('message', ''),
                utm_source=request.data.get('utm_source'),
                utm_medium=request.data.get('utm_medium'),
                utm_campaign=request.data.get('utm_campaign'),
                page_url=request.data.get('page_url'),
                client_id=request.data.get('client_id'),
                device_type=request.data.get('device_type', 'desktop'),
                language=request.data.get('language', 'en')
            )
            
            serializer = LeadSerializer(lead)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='create_callback/(?P<project_id>[^/.]+)')
    def create_callback(self, request, project_id=None):
        """Создание заявки на звонок через виджет"""
        try:
            project = get_object_or_404(Project, id=project_id)
            channel_id = request.data.get('channel')
            if channel_id:
                channel = get_object_or_404(Channel, id=channel_id)
            else:
                # Создаем дефолтный канал для звонков
                channel, created = Channel.objects.get_or_create(
                    project=project,
                    type='call',
                    defaults={
                        'label': 'Заказ звонка',
                        'priority': 2,
                        'is_active': True
                    }
                )
            
            callback = CallbackRequest.objects.create(
                project=project,
                channel=channel,
                contact=request.data.get('contact', ''),
                message=request.data.get('message', ''),
                preferred_time=request.data.get('preferred_time'),
                page_url=request.data.get('page_url'),
                client_id=request.data.get('client_id'),
                device_type=request.data.get('device_type', 'desktop'),
                language=request.data.get('language', 'en')
            )
            
            serializer = CallbackRequestSerializer(callback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='start_chat/(?P<project_id>[^/.]+)')
    def start_chat(self, request, project_id=None):
        """Начало чат-сессии через виджет"""
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # Создаем новую сессию чата
            session = ChatSession.objects.create(
                project=project,
                client_id=request.data.get('client_id'),
                page_url=request.data.get('page_url'),
                device_type=request.data.get('device_type', 'desktop'),
                language=request.data.get('language', 'en')
            )
            
            # Добавляем приветственное сообщение
            welcome_message = ChatMessage.objects.create(
                session=session,
                content="Добро пожаловать! Как мы можем вам помочь?",
                message_type='system'
            )
            
            serializer = ChatSessionSerializer(session)
            data = serializer.data
            data['messages'] = [ChatMessageSerializer(welcome_message).data]
            
            return Response(data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='send_message/(?P<project_id>[^/.]+)')
    def send_message(self, request, project_id=None):
        """Отправка сообщения в чат через виджет"""
        try:
            session_id = request.data.get('session_id')
            if not session_id:
                return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            session = get_object_or_404(ChatSession, id=session_id)
            
            # Создаем сообщение от пользователя
            message = ChatMessage.objects.create(
                session=session,
                content=request.data.get('content', ''),
                message_type=request.data.get('message_type', 'user')
            )
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)