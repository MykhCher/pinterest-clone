from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.generic import FormView, TemplateView, View
from django.views.generic.detail import DetailView
from .forms import CustomUserCreationForm, UserLoginForm
from .models import Profile, ForgotPassword

User = get_user_model()


class EmailVerify(View):
    """Verify account via email message token, generated and 
    sent by `RegisterFormView.send_activation_email()`
    """

    def get(self, request: HttpRequest, uidb64: bytes | str, token: str) -> HttpResponseRedirect:
        acc_activation_token = PasswordResetTokenGenerator()
        try:
            uid = force_bytes(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except:
            user = None

        if user is not None and acc_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect('login')
        else:
            return redirect('placeholder')


class RegisterFormView(FormView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "register.html"


    # def send_activation_email(self, request: HttpRequest, user: User, to_email: str) -> int:
    #     """Send mail with user verification token to the `to_email` address."""
    #     acc_activation_token = PasswordResetTokenGenerator()
    #     email = EmailMessage(
    #         subject='Activate your user account', 
    #         body=render_to_string(
    #             template_name="acc_activate_email.html",
    #             context={
    #                 'user': user,
    #                 'domain': get_current_site(request).domain,
    #                 'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
    #                 'token' : acc_activation_token.make_token(user),
    #                 'protocol' : 'https' if request.is_secure() else 'http'
    #             }
    #         ),
    #         to=[to_email]
    #     )
    #     return email.send() 


    def form_valid(self, form):
        user = form.save(commit=False)
        # user.is_active = False
        user.save()
        # self.send_activation_email(
        #     request=self.request,
        #     user=user,
        #     to_email=form.cleaned_data.get("email"),
        # )
        return super().form_valid(form)
    

class UserLoginView(FormView):
    form_class = UserLoginForm
    success_url = reverse_lazy("placeholder")
    template_name = "login.html"

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        errors = form.errors['__all__']
        print(errors)
        return super().form_invalid(form)


class LogoutView(View):

    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        logout(request)
        return redirect('login')
    

class ProfileView(DetailView):
    model = Profile
    template_name = "profile_detail.html"
    slug_field = "user__username"
    slug_url_kwarg = "user__username"


class SendOTPView(View):
    template_name = "otp_sent.html"

    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        try:
            user = User.objects.get(email=request.POST.get('email'))
            ForgotPassword.objects.create(user=user)
        except Exception as e:
            return render(request, 'placeholder.html', {'message' : e})
        
        forgot_password_obj = ForgotPassword.objects.filter(user=user).first()
        forgot_password_obj.is_user_password_updated = True
        forgot_password_obj.save()

        return render(request, self.template_name, {})
    

class ForgotPasswordView(TemplateView):
    """Post an email adress to be one-time code receiver."""
    template_name = "forgot_pass.html"
    

class PlaceholderView(TemplateView):
    """A placeholder view, temporary used to be a redirection target."""
    template_name = "placeholder.html"
