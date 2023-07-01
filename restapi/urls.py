from django.urls import path
from rest_framework import routers

from restapi import views

router = routers.DefaultRouter()

router.register(r'my_pins', views.MyPinViewSet, basename='api-pins')
router.register(r'pins', views.AllPinsViewset, basename='api-all-pins')
router.register(r'profile', views.ProfileViewset, basename='profiles')

urlpatterns = [
    path("pin_in_board/<int:pin_pk>/<str:board_name>/", views.PinToBoard.as_view(), name="pin_in_board"),
]

