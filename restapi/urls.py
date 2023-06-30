from rest_framework import routers

from restapi import views

router = routers.DefaultRouter()
router.register(r'my_pins', views.MyPinViewSet, basename='api-pins')
router.register(r'pins', views.AllPinsViewset, basename='api-all-pins')
