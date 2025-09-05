from rest_framework import serializers
from .models import Channel, Lead

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = "__all__"

class LeadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = "__all__"
