from rest_framework import viewsets
from .models import ABTest, ABTestVariant, UserVariant
from .serializers import ABTestSerializer, ABTestVariantSerializer, UserVariantSerializer


class ABTestViewSet(viewsets.ModelViewSet):
    queryset = ABTest.objects.all()
    serializer_class = ABTestSerializer


class ABTestVariantViewSet(viewsets.ModelViewSet):
    queryset = ABTestVariant.objects.all()
    serializer_class = ABTestVariantSerializer


class UserVariantViewSet(viewsets.ModelViewSet):
    queryset = UserVariant.objects.all()
    serializer_class = UserVariantSerializer
