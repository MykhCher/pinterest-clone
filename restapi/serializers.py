from rest_framework import serializers

from pins.models import Pin


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = ['pk', 'user', 'title', 'description', 'file', 'get_type']
