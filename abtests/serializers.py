from rest_framework import serializers
from .models import ABTest, ABTestVariant, UserVariant


class ABTestVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ABTestVariant
        fields = '__all__'


class ABTestSerializer(serializers.ModelSerializer):
    variants = ABTestVariantSerializer(many=True, read_only=True)

    class Meta:
        model = ABTest
        fields = '__all__'


class UserVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVariant
        fields = '__all__'
