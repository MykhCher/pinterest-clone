from typing import Any
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView

from .forms import CreatePinForm, EditPinForm
from .models import Pin


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