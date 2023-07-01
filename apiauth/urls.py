from django.urls import path
from .views import signin

urlpatterns = [
    path('get_token', signin, name='get_token'),
]