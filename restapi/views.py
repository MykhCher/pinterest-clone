from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db.models.query import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework import viewsets, permissions, views
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from .serializers import (PinSerializer, 
                          ProfileSerializer, 
                          ProfileEditSerializer, 
                          BoardSerializer,
                          BoardCreateSerializer,
                          CommentSerializer,
                          CommentEditSerializer,
                          )
from accounts.models import Profile, Follow
from pins.models import Pin, Comment
from boards.models import Board

# Set up time-to-live for cache.
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
 

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
    
    @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self, request, *args, **kwargs) -> Response:
        return super().retrieve(request, *args, **kwargs)
    

class AllPinsViewset(viewsets.ReadOnlyModelViewSet):
    """
    Retreive data about all the pins. Read-only.
    """
    queryset = Pin.objects.all().order_by("-date_created")
    serializer_class = PinSerializer
    pagination_class = PageNumberPagination
    max_page_size = 100

    @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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
    

class ProfileViewset(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('pk')
    permitted_actions = ['list', 'retrieve', 'partial_update']
    pagination_class = PageNumberPagination
    serializer_class = ProfileSerializer
    edit_serializer = ProfileEditSerializer
    max_page_size = 100

    def get_permissions(self) -> list:
        """
        Allow actions mentioned in `self.permitted_actions` only. 
        """
        if self.action not in self.permitted_actions:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    def partial_update(self, request: Request, pk: int, format=None) -> Response:
        instance = self.get_object()

        # Check if requested user owns this profile.
        if instance.user != request.user:
            return Response({"message" : "You are not allowed to do this!"}, 403)
        
        # Serialize recieved data, update profile.
        serializer = self.edit_serializer(instance, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        data = self.serializer_class(instance).data
        data.setdefault("message", "Profile successfully updated!")
        return Response(data)
    
    @method_decorator(cache_page(CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class FollowEndpoint(views.APIView):

    def post(self, request: Request, format=None) -> Response:
        """
        Follow given user.
        """
        try:
            followed = get_user_model().objects.get(username=request.data.get('username'))
            follower = request.user
        except get_user_model().DoesNotExist:
            message = {"message": "Username query didn't give any results."}
            return Response(data=message, status=404)

        response = {
            "user": followed.username,
            "new_follower": follower.username,
        }
        follow_obj = Follow.objects.filter(follower=follower, following=followed)

        if not follow_obj.exists():
            Follow.objects.create(follower=follower, following=followed)
            response.setdefault("message", "Now you are following %s." % followed.username)
            status_code = 201   # Created
        else:
            response.setdefault("message", "Condition already satisfied.")
            status_code = 200   # OK

        return Response(response, status_code)
    
    def delete(self, request: Request, format = None) -> Response:
        """
        Unfollow thhe user.
        """
        try:
            followed = get_user_model().objects.get(username=request.data.get('username'))
            follower = request.user
        except get_user_model().DoesNotExist:
            message = {"message": "Username query didn't give any results."}
            return Response(data=message, status=404)

        response = {
            "user": followed.username,
            "new_follower": follower.username,
        }
        follow_obj = Follow.objects.filter(follower=follower, following=followed)

        if follow_obj.exists():
            follow_obj.delete()
            response.setdefault("message", "Now you are not following %s." % followed.username)
            status_code = 204   # No content
        else:
            response.setdefault("message", "Condition already satisfied.")
            status_code = 200   # OK

        return Response(response, status_code)


class BoardViewset(viewsets.ModelViewSet):
    queryset = Board.objects.all().order_by('-id')
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = PageNumberPagination
    serializer_class = BoardSerializer
    max_page_size = 100

    def create(self, request: Request, format = None, *args, **kwargs) -> Response:
        """
        Create a board, owned by a request user.
        """
        data = request.data.copy()
        data.setdefault("user", request.user.pk)

        serializer = BoardCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, 201)
    
    def destroy(self, request: Request, pk: int, *args, **kwargs) -> Response:
        """
        Response for DELETE requests.
        """

        # Retrieve and delete object.
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response(
            data={
                "title" : instance.title,
                "message" : "Board successfully removed."
            },
        )

    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Provide response for PATCH requests.
        """

        # Enable partial updates.
        partial = kwargs.setdefault('partial', True)

        # Retrieve object.
        instance = self.get_object()

        # Serialize and edit object.
        serializer = BoardCreateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Return response with serialized object data.
        return Response(data=serializer.data)
    

class CommentByUser(views.APIView):
    model = Comment
    serializer_class = CommentSerializer
    edit_serializer_class = CommentEditSerializer
    permission_classes = [permissions.IsAuthenticated, ]
    
    def get_queryset(self) -> QuerySet:
        """
        Get QuerySet of all Comments made by request user.
        """
        user = self.request.user
        return self.model.objects.filter(user=user)
    
    def get(self, request: Request, pk: int | None = None, format=None) -> Response:
        """
        Get a list of comments made by a user.
        If `pk` attribute was provided, then retrieve exact comment.
        """
        queryset = self.get_queryset()

        # Retrieve and return single comment if pk was provided.
        if pk is not None:

            try:
                queryset = queryset.get(pk=pk)
                serializer = self.serializer_class(queryset)
            except self.model.DoesNotExist:
                data = {"message": "Comment with id=%s was not found." % pk}
                return Response(data=data, status=404)
        
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def delete(self, request: Request, pk: int, format=None) -> Response:
        """
        Delete given comment.
        """
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            data = {"message": "Comment with id=%s was not found." % pk}
            return Response(data=data, status=404)

        instance.delete()
        return Response(status=204)

    def patch(self, request: Request, pk: int, format=None) -> Response:
        """
        Edit given comment's text.
        """
        try:
            instance = self.get_queryset().get(pk=pk)
        except self.model.DoesNotExist:
            data = {"message": "Comment with id=%s was not found." % pk}
            return Response(data=data, status=404)
        
        # Validate data, commit changes.
        serializer = self.edit_serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Set up response output.
        response = {
            'id': pk,
            'text': instance.text,
            'user': instance.user.username,
            'message': 'Comment was successfully edited.',
        }

        return Response(data=response, status=200)
    

class CommentPin(views.APIView):
    model = Comment
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_queryset(self, pk: int) -> QuerySet:
        return Pin.objects.get(pk=pk).comments.all()
    
    @method_decorator(cache_page(CACHE_TTL))
    def get(self, request: Request, pk: int, format=None) -> Response:
        """
        List all the comments under given pin.
        """
        queryset = self.get_queryset(pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(data=serializer.data)
    
    def post(self, request: Request, pk: int, format=None) -> Response:
        """
        Comment given pin.
        """

        # Check if there is Pin with provided pk.
        try:
            if not 'pin' in request.data:
                pin_pk = Pin.objects.get(pk=pk).pk
            else:
                pin_pk = Pin.objects.get(pk=request.data.get('pin')).pk
        except Pin.DoesNotExist:
            data = {"message": "Pin with id=%s was not found." % pk}
            return Response(data=data, status=404)

        # Restrict passing another user pk into post-data.
        if 'user' in request.data:
            data = {"message": "You should not provide any info about user."}
            return Response(data=data, status=403)
        
        # Retrieve post-data, insert info about user and pin into it.
        data = request.data.copy()
        data.setdefault('user', request.user.pk)
        data.setdefault('pin', pin_pk)

        # Create comment with given data.
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=201)
