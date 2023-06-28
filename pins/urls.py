from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.CreatePinView.as_view(), name="create_pin"),
    path('<str:username>/created/', views.CreatedPins.as_view(), name='created_pins'),
]