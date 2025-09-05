from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from datetime import datetime, time
import pytz
from .models import ProjectConfig, Channel, Schedule, Lead, CallbackRequest
from .serializers import (
    ProjectConfigSerializer, ChannelSerializer, ScheduleSerializer, 
    LeadSerializer, CallbackRequestSerializer, WidgetConfigSerializer
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
        is_online = self._is_online(project)
        
        channels = project.channels.filter(is_active=True)
        
        if is_online:
            if device_type == 'mobile':
                channels = channels.filter(type__in=['call', 'callback']).order_by('priority')
            else:
                channels = channels.filter(type__in=['chat', 'messenger', 'form']).order_by('priority')
        else:
            channels = channels.filter(type__in=['form', 'chat', 'messenger']).order_by('priority')
        
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
        
        serializer = LeadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

