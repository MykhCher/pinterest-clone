from django.urls import path
from .views import RegisterFormView, PlaceholderView, EmailVerify, UserLoginView

urlpatterns = [
    path("register/", RegisterFormView.as_view(), name="profile_register"),
    path("placeholder/", PlaceholderView.as_view(), name="placeholder"),
    path("activate/<uidb64>/<token>/", EmailVerify.as_view(), name="activate"),
    path("login/", UserLoginView.as_view(), name="login")
]
