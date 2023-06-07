from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterFormView.as_view(), name="profile_register"),
    path("placeholder/", views.PlaceholderView.as_view(), name="placeholder"),
    path("activate/<uidb64>/<token>/", views.EmailVerify.as_view(), name="activate"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('profile/<str:user__username>', views.ProfileView.as_view(), name="profile"),
    path('sent_otp', views.SendOTPView.as_view(), name="send_otp"),
    path('forgot_pass', views.ForgotPasswordView.as_view(), name="forgot"),
]
