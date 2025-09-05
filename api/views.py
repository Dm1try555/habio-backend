from rest_framework import viewsets
from .models import Channel, Lead
from .serializers import ChannelSerializer, LeadSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
