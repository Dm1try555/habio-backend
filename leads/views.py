from rest_framework import viewsets
from .models import Lead, CallbackRequest
from .serializers import LeadSerializer, CallbackRequestSerializer


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class CallbackRequestViewSet(viewsets.ModelViewSet):
    queryset = CallbackRequest.objects.all()
    serializer_class = CallbackRequestSerializer
