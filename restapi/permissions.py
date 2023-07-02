from django.db import models
from rest_framework import permissions, views
from rest_framework.request import Request

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request: Request, view: views.View, obj: models.Model) -> bool:
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance-level permission to only allow the owner of the object to edit it.
        return obj.user == request.user
