from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.CreatePinView.as_view(), name="create_pin"),
    path('<str:username>/created/', views.CreatedPins.as_view(), name='created_pins'),
    path("edit/<int:pk>", views.EditPinView.as_view(), name="edit_pin"),
    path("<int:pk>", views.DetailPinView.as_view(), name="pin_detail"),
    path("comment/<int:pk>", views.CreateCommentView.as_view(), name="add_comment"),
    path("comment_remove/<int:pk>", views.DeleteCommentView.as_view(), name="delete_comment"),
]