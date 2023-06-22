from typing import Any, Dict
from django.core.exceptions import (ImproperlyConfigured, 
                                    ObjectDoesNotExist, 
                                    MultipleObjectsReturned,
                                    PermissionDenied)
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import (HttpResponseRedirect, 
                        HttpRequest, 
                        HttpResponse, 
                        Http404)
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render, resolve_url
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.views.generic import FormView, TemplateView, UpdateView, View
from django.views.generic.detail import DetailView

from .forms import (CustomUserCreationForm, 
                    UserLoginForm, 
                    CustomPasswordResetForm,
                    EditProfileForm)
from .models import Profile, ForgotPassword
from .models import Follow as FollowModel   # to not be confued with Follow view on line 140
from boards.forms import CreateBoardForm


User = get_user_model()


class EmailVerify(View):
    """Verify account via email message token, generated and 
    sent by `send_confirmation_email()` signal.
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

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        return super().form_valid(form)
    
class UserLoginView(FormView):
    form_class = UserLoginForm
    success_url = reverse_lazy("home")
    template_name = "login.html"

    def form_valid(self, form) -> HttpResponseRedirect:
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        # Check if redirected from LoginRequiredMixin-inherited view.
        redirect_from_loginmixin = self.request.GET.get("next")

        if redirect_from_loginmixin:
            return redirect_from_loginmixin
        
        return super().get_success_url()

class LogoutView(LoginRequiredMixin, View):
    login_url = reverse_lazy("login")

    def get(self, request: HttpRequest) -> HttpResponseRedirect:
        logout(request)
        return redirect('login')
    
    def handle_no_permission(self) -> HttpResponseRedirect:
        """Overwrite base method in order not to redirect back."""
        if self.raise_exception or self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())
        
        resolved_login_url = resolve_url(self.get_login_url())
        path = self.request.get_full_path()

        return redirect_to_login(
            path,
            resolved_login_url,
        )

    

class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profile_detail.html"
    slug_field = "user__username"
    slug_url_kwarg = "user__username"
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get_context_object_name(self, obj: Profile) -> str:
        return "profile"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.get_object().user

        context['is_following'] = self.request.user.followers.filter(following=user).first()
        context['create_board_form'] = CreateBoardForm()

        return context
    
class EditProfile(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = EditProfileForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('profile')
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse("profile", kwargs={"user__username": user.username})

    def get_object(self, queryset=None) -> Profile:
        # Return the current user's profile
        return self.request.user.profile

    def get_initial(self) -> Dict[str, Any]:
        initial = super().get_initial()
        user = self.request.user
        new_initial = {
            'first_name' : user.profile.first_name,
            'last_name' : user.profile.last_name,
            'description' : user.profile.description,
            'sex' : user.profile.sex,
            'profile_status' : user.profile.profile_status,
        }
        initial.update(new_initial)
        return initial
    

class Follow(LoginRequiredMixin, View):
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get(self, request: HttpRequest, username: str) -> HttpResponseRedirect:
        # Retrieve user from database, using username.
        try:
            user = User.objects.get(username=username)
        except (ObjectDoesNotExist, MultipleObjectsReturned,):
            raise Http404
        
        if user == request.user:
            messages.error(request, 'You can\'t follow yourself.')
            return redirect(request.META.get('HTTP_REFERER'))
        
        # Check if user already follows.
        check_follow = FollowModel.objects.filter(following=user, follower=request.user)
        
        if check_follow.exists():
            messages.error(request, 'You already follow %s' % user.username)
            return redirect(request.META.get('HTTP_REFERER'))
        
        follow = FollowModel.objects.create(following=user, follower=request.user)
        follow.save()
        return redirect(request.META.get('HTTP_REFERER'))
    
class Unfollow(LoginRequiredMixin, View):
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get(self, request: HttpRequest, username: str) -> HttpResponseRedirect:
        try:
            user = User.objects.get(username=username)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            raise Http404
        
        FollowModel.objects.filter(following=user, follower=request.user).delete()
        return redirect(request.META.get('HTTP_REFERER'))


class SendOTPView(View):
    template_name = "otp_sent.html"

    def post(self, request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
        try:
            user = User.objects.get(email=request.POST.get('email'))
            ForgotPassword.objects.create(user=user)
        except Exception as e:
            return render(request, 'placeholder.html', {'message' : e})
        
        forgot_password_obj = ForgotPassword.objects.filter(user=user).last()
        forgot_password_obj.is_user_password_updated = True
        forgot_password_obj.save()

        return render(request, self.template_name, {"email": user.email})
    
class ChangePasswordView(FormView):
    """Password reset form-view."""
    form_class = CustomPasswordResetForm
    template_name = 'change_pass.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse | HttpResponseRedirect:
        """Handling GET and POST methods."""

        # Check for keyword arguments in url.
        if "uidb64" not in kwargs or "token" not in kwargs:
            raise ImproperlyConfigured(
                "The URL path must contain 'uidb64' and 'token' parameters."
            )

        # Search for user, using given in url-kwargs user id (uid).
        uidb64 = urlsafe_base64_decode(kwargs['uidb64'])
        self.user = User.objects.get(id=uidb64)

        if self.user is not None:
            token = kwargs['token']
            # Handle posted form data.
            if request.method.lower() == 'post':
                form = CustomPasswordResetForm(user=self.user, data=request.POST)
                if form.is_valid():
                    return self.form_valid(form)
                elif not form.is_valid():
                    return self.form_invalid(form)
                
            code = self.user.forgot_pass.last()
            if token == code.forget_password_otp and timezone.now() <= code.created_at + timezone.timedelta(minutes=10):
                # If tokens match and it haven't expired yet, display the password reset form.
                form = CustomPasswordResetForm(user=self.user)
                context = self.get_context_data(form=form)
                return self.render_to_response(context)
        
        # Return to email sending page, if something went wrong.
        return redirect('forgot')
        

    def form_valid(self, form: CustomPasswordResetForm) -> HttpResponse:
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form: CustomPasswordResetForm) -> HttpResponse:
        print(form.error_messages)
        return super().form_invalid(form)

class CheckOTP(View):
    """Transition view, used to validate the OTP and check for its expiration date."""

    def post(self, request: HttpRequest) -> HttpResponseRedirect:
        otp = request.POST.get('otp') # Get 4-digit code from the request.

        # Retrieve the user based on entered code.
        try:
            users_by_code = User.objects.filter(forgot_pass__forget_password_otp=otp)
            user_by_email = User.objects.get(email=request.POST.get('sent_email'))
        except User.DoesNotExist as e:
            return redirect('forgot')
        
        # Check if code matches the previous user email query.
        if user_by_email in users_by_code:
            user = user_by_email
            code = user.forgot_pass.last()
        else:
            return redirect('forgot')
        
        # Check if 10-minute code expiration interval has passed. 
        if timezone.now() <= code.created_at + timezone.timedelta(minutes=10):
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            safe_code = code.forget_password_otp
            return redirect('change_pass', uidb64=uidb64, token=safe_code)

class ForgotPasswordView(TemplateView):
    """Post an email adress to be one-time code receiver."""
    template_name = "forgot_pass.html"
    

class PlaceholderView(TemplateView):
    """A placeholder view, temporary used to be a redirection target."""
    template_name = "placeholder.html"
