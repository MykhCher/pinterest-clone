from rest_framework import routers

from .views import PinViewSet

router = routers.DefaultRouter()
router.register(r'pins', PinViewSet, basename='api-pins')
