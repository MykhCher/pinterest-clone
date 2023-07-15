from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

urlpatterns = [
    path("register/", views.RegisterFormView.as_view(), name="profile_register"),
    path("login/", views.UserLoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),

    path("placeholder/", views.PlaceholderView.as_view(), name="placeholder"),
    path('profile/<str:user__username>', cache_page(60)(views.ProfileView.as_view()), name="profile"),
    path('edit_profile', views.EditProfile.as_view(), name="edit_profile"),

    path('follow/<str:username>', views.Follow.as_view(), name='follow'),
    path('unfollow/<str:username>', views.Unfollow.as_view(), name='unfollow'),

    path("activate/<uidb64>/<token>/", views.EmailVerify.as_view(), name="activate"),

    path('sent_otp', views.SendOTPView.as_view(), name="send_otp"),
    path('check_otp', views.CheckOTP.as_view(), name="check_otp"),
    path('forgot_pass', views.ForgotPasswordView.as_view(), name="forgot"),
    path('change_pass/<str:uidb64>/<str:token>', views.ChangePasswordView.as_view(), name="change_pass"),
]
