from django.urls import path
from . import views 

urlpatterns = [
    path("create", views.CreateBoardView.as_view(), name="create_board"),
    path("edit/<str:name>", views.EditBoardView.as_view(), name="edit_board"),
    path("<str:board_name>", views.DetailBoardView.as_view(), name="board_detail"),
    path("save_to_board/<int:pk>", views.SaveToBoard.as_view(), name="save_to_board"),
]
