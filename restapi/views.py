from rest_framework import viewsets, permissions

from pins.models import Pin
from .serializers import PinSerializer
 

class PinViewSet(viewsets.ModelViewSet):
    """
    Test API endpoint to check how we retrieve data about Pins.
    """
    queryset = Pin.objects.all()
    serializer_class = PinSerializer
    permission_classes = [permissions.IsAuthenticated]
