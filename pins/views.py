from typing import Any, Dict
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from .forms import CreatePinForm, EditPinForm
from .models import Pin
from boards.forms import CreateBoardForm
from accounts.models import Profile


User = get_user_model()


class CreatePinView(LoginRequiredMixin, CreateView):
    model = Pin
    template_name = "create_pin.html"
    form_class = CreatePinForm
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse("profile", kwargs={"user__username":user.username})

    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass the instance of user, that made request, into a form."""
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs
    
class EditPinView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Pin
    form_class = EditPinForm
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        """Redirect back from where request was made."""
        return self.request.META.get('HTTP_REFERER')

    def test_func(self) -> bool:
        """Method from `UserPassesTestMixin`. Test if 
        user that made request is object's owner.
        """
        obj = self.get_object()
        return obj.user == self.request.user

class DeletePinView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pin
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse("profile", kwargs={"user__username":user.username})
    
    def test_func(self) -> bool:
        """Method from `UserPassesTestMixin`. Tests if user, 
        that made request is object's owner.
        """
        obj = self.get_object()
        return obj.user == self.request.user
    
class CreatedPins(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profile_detail.html"
    slug_field = "user__username"
    slug_url_kwarg = "username"
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get_context_object_name(self, obj: Profile) -> str:
        return "profile"
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.get_object().user
        pins = user.pin_user.all()

        new_context = {
            'is_following': self.request.user.followers.filter(following=user).first(),
            'create_board_form': CreateBoardForm(),
            'created_pins': pins,
        }

        context.update(new_context)

        return context