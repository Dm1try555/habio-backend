from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from datetime import datetime, time
import pytz
from .models import ProjectConfig, Channel, Schedule, Lead, CallbackRequest, ChatSession, ChatMessage
from .serializers import (
    ProjectConfigSerializer, ChannelSerializer, ScheduleSerializer, 
    LeadSerializer, CallbackRequestSerializer, WidgetConfigSerializer,
    ChatSessionSerializer, ChatMessageSerializer
)

class ProjectConfigViewSet(viewsets.ModelViewSet):
    queryset = ProjectConfig.objects.all()
    serializer_class = ProjectConfigSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class CallbackRequestViewSet(viewsets.ModelViewSet):
    queryset = CallbackRequest.objects.all()
    serializer_class = CallbackRequestSerializer

class ChatSessionViewSet(viewsets.ModelViewSet):
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

class WidgetAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = ProjectConfig.objects.filter(is_active=True)
    serializer_class = WidgetConfigSerializer

    @action(detail=True, methods=['get'])
    def config(self, request, pk=None):
        project = self.get_object()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def channels(self, request, pk=None):
        project = self.get_object()
        device_type = request.query_params.get('device', 'desktop')
        prefer_channel = request.query_params.get('prefer')
        last_used = request.query_params.get('last_used')
        is_online = self._is_online(project)
        
        channels = project.channels.filter(is_active=True)
        
        # Apply business priority override
        if prefer_channel:
            channels = channels.filter(type=prefer_channel)
        else:
            # Apply smart routing logic - always show call and callback in top
            if is_online:
                if device_type == 'mobile':
                    # Mobile: call/callback first, then others
                    call_channels = channels.filter(type__in=['call', 'callback']).order_by('priority')
                    other_channels = channels.exclude(type__in=['call', 'callback']).order_by('priority')
                    channels = list(call_channels) + list(other_channels)
                else:
                    # Desktop: call/callback first, then chat/messenger/form
                    call_channels = channels.filter(type__in=['call', 'callback']).order_by('priority')
                    other_channels = channels.filter(type__in=['chat', 'messenger', 'form']).order_by('priority')
                    channels = list(call_channels) + list(other_channels)
            else:
                # Offline: form/chat first, then call/callback with badge
                form_channels = channels.filter(type__in=['form', 'chat', 'messenger']).order_by('priority')
                call_channels = channels.filter(type__in=['call', 'callback']).order_by('priority')
                channels = list(form_channels) + list(call_channels)
        
        # Apply personal memory (last used channel gets priority)
        if last_used and not prefer_channel:
            try:
                last_used_id = int(last_used)
                last_used_channel = channels.filter(id=last_used_id).first()
                if last_used_channel:
                    # Move last used channel to top
                    other_channels = channels.exclude(id=last_used_id)
                    channels = [last_used_channel] + list(other_channels)
            except (ValueError, TypeError):
                pass
        
        serializer = ChannelSerializer(channels, many=True)
        return Response({
            'channels': serializer.data,
            'is_online': is_online,
            'next_available': self._get_next_available_time(project)
        })

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def create_lead(self, request, pk=None):
        project = self.get_object()
        data = request.data.copy()
        data['project'] = project.id
        
        print(f"Creating lead with data: {data}")
        
        serializer = LeadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def create_callback(self, request, pk=None):
        project = self.get_object()
        data = request.data.copy()
        data['project'] = project.id
        
        serializer = CallbackRequestSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def _is_online(self, project):
        now = timezone.now()
        project_tz = pytz.timezone(project.timezone)
        local_time = now.astimezone(project_tz)
        current_day = local_time.strftime('%A').lower()
        current_time = local_time.time()
        
        schedules = project.schedules.filter(
            day=current_day,
            is_working_day=True,
            start_time__lte=current_time,
            end_time__gte=current_time
        )
        
        return schedules.exists()

    def _get_next_available_time(self, project):
        now = timezone.now()
        project_tz = pytz.timezone(project.timezone)
        local_time = now.astimezone(project_tz)
        
        for i in range(7):
            check_date = local_time.date() + timezone.timedelta(days=i)
            day_name = check_date.strftime('%A').lower()
            
            schedules = project.schedules.filter(
                day=day_name,
                is_working_day=True
            ).order_by('start_time')
            
            if schedules.exists():
                schedule = schedules.first()
                if i == 0 and local_time.time() < schedule.start_time:
                    return f"{check_date} {schedule.start_time}"
                elif i > 0:
                    return f"{check_date} {schedule.start_time}"
        
        return None

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def start_chat(self, request, pk=None):
        project = self.get_object()
        client_id = request.data.get('client_id')
        page_url = request.data.get('page_url', '')
        
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(
            project=project,
            client_id=client_id,
            defaults={'page_url': page_url, 'is_active': True}
        )
        
        if created:
            # Add welcome message
            ChatMessage.objects.create(
                session=session,
                message_type='system',
                content='Добро пожаловать! Как мы можем вам помочь?'
            )
        
        serializer = ChatSessionSerializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def chat_messages(self, request, pk=None):
        project = self.get_object()
        client_id = request.query_params.get('client_id')
        
        try:
            session = ChatSession.objects.get(
                project=project,
                client_id=client_id,
                is_active=True
            )
            messages = session.messages.all()
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def send_message(self, request, pk=None):
        project = self.get_object()
        client_id = request.data.get('client_id')
        content = request.data.get('content')
        message_type = request.data.get('message_type', 'user')
        
        try:
            session = ChatSession.objects.get(
                project=project,
                client_id=client_id,
                is_active=True
            )
            
            message = ChatMessage.objects.create(
                session=session,
                message_type=message_type,
                content=content
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            serializer = ChatMessageSerializer(message)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ChatSession.DoesNotExist:
            return Response({'error': 'Chat session not found'}, status=status.HTTP_404_NOT_FOUND)

