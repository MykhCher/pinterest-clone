from django.db.models.query import QuerySet

from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination

from pins.models import Pin
from .serializers import PinSerializer
 

class MyPinViewSet(viewsets.ModelViewSet):
    """
    Retreive, list or delete user's pins.
    """
    serializer_class = PinSerializer
    permitted_actions = ['list', 'retrieve', 'destroy']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        return Pin.objects.filter(user=self.request.user)
    
    def get_permissions(self) -> list:
        """
        Allow actions mentioned in `self.permitted_actions` only. 
        """

        if self.action not in self.permitted_actions:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]
    

class AllPinsViewset(viewsets.ReadOnlyModelViewSet):
    """
    Retreive data about all the pins. Read-only.
    """
    queryset = Pin.objects.all().order_by("-date_created")
    serializer_class = PinSerializer
    pagination_class = PageNumberPagination
    max_page_size = 100
