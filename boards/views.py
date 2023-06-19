from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView

from .forms import CreateBoardForm
from .models import Board


class CreateBoardView(LoginRequiredMixin, FormView):
    form_class = CreateBoardForm
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse('profile', kwargs={"user__username":user.username})