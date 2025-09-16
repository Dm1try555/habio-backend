from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .serializers import ChatSessionSerializer, ChatMessageSerializer
from projects.models import Project


class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.all()
        return Response(ChatMessageSerializer(messages, many=True).data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def start_chat(self, request):
        """Начало чат-сессии через виджет"""
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
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


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def send_message(self, request):
        """Отправка сообщения в чат через виджет"""
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            session = get_object_or_404(ChatSession, id=session_id)
            
            # Создаем сообщение от пользователя
            message = ChatMessage.objects.create(
                session=session,
                content=request.data.get('content', ''),
                message_type=request.data.get('message_type', 'user')
            )
            
            # Здесь можно добавить логику для автоматических ответов
            # или уведомления администраторов
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
