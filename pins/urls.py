from django.conf import settings
from django.views.decorators.cache import cache_page
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.urls import path
from . import views


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


urlpatterns = [
    path("create/", views.CreatePinView.as_view(), name="create_pin"),
    path('<str:username>/created/', views.CreatedPins.as_view(), name='created_pins'),
    path("edit/<int:pk>", views.EditPinView.as_view(), name="edit_pin"),
    path("<int:pk>", cache_page(CACHE_TTL)(views.DetailPinView.as_view()), name="pin_detail"),
    path("comment/<int:pk>", views.CreateCommentView.as_view(), name="add_comment"),
    path("comment_remove/<int:pk>", views.DeleteCommentView.as_view(), name="delete_comment"),
]