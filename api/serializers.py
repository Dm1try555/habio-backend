from rest_framework import serializers
from .models import ProjectConfig, Channel, Schedule, Lead, CallbackRequest

class ProjectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectConfig
        fields = "__all__"

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"

class CallbackRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = "__all__"

class WidgetConfigSerializer(serializers.ModelSerializer):
    channels = ChannelSerializer(many=True, read_only=True)
    schedules = ScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProjectConfig
        fields = ['id', 'name', 'timezone', 'channels', 'schedules']
