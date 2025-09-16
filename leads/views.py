from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Lead, CallbackRequest
from .serializers import LeadSerializer, CallbackRequestSerializer
from projects.models import Project
from channels.models import Channel


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_lead(self, request):
        """Создание лида через виджет"""
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
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


class CallbackRequestViewSet(viewsets.ModelViewSet):
    queryset = CallbackRequest.objects.all()
    serializer_class = CallbackRequestSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def create_callback(self, request):
        """Создание заявки на звонок через виджет"""
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
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
