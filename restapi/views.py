from django.db.models.query import QuerySet

from rest_framework import viewsets, permissions, views
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.models import Profile
from pins.models import Pin
from boards.models import Board
from .serializers import PinSerializer, ProfileSerializer
 

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


class PinToBoard(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self) -> QuerySet:
        queryset = Pin.objects.all()
        return queryset
        
    def get(self, request: Request, pin_pk: int, board_name: str, format=None) -> Response:
        """
        Add this pin into chosen board.
        If pin is already in the board, return "Already in board" message.
        """
        pin = Pin.objects.get(pk=pin_pk)
        board = Board.objects.get(title=board_name)

        # Check if user owns given board.
        if board.user != request.user:
            data = {"message": "You are not allowed to save into this board."}
            return Response(data=data,status=403,)

        if pin not in board.pins.all():
            board.pins.add(pin)
            response = {
                "pin": PinSerializer(pin).data,
                "board_title": board.title,
                "message": "Pin successfully added to the board.",
            }
        else:
            response = {
                "message": "Already in board."
            }
        return Response(response)
    
    def delete(self, request: Request, pin_pk: int, board_name: str, format=None) -> Response:
        """
        Remove this pin from given board.
        If pin is not in the board, return 
        "Pin is not found in given board" message.
        """
        pin = Pin.objects.get(pk=pin_pk)
        board = Board.objects.get(title=board_name)

        # Check if user owns given board.
        if board.user != request.user:
            data = {"message": "You are not allowed to change this board."}
            return Response(data=data,status=403,)

        if pin in board.pins.all():
            board.pins.remove(pin)
            response = {
                "pin": PinSerializer(pin).data,
                "board_title": board.title,
                "message": "Pin successfully removed from the board.",
            }
        else:
            response = {
                "message": "Pin is not found in given board."
            }
        return Response(response)
    

class ProfileViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all().order_by('pk')
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    serializer_class = ProfileSerializer    
    max_page_size = 100