from typing import Any
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, DetailView

from .forms import CreateBoardForm, EditBoardForm
from .models import Board


class CreateBoardView(LoginRequiredMixin, CreateView):
    model = Board
    form_class = CreateBoardForm
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse('profile', kwargs={"user__username":user.username})
    
    def form_valid(self, form: CreateBoardForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)


class EditBoardView(LoginRequiredMixin, UpdateView):
    model = Board
    form_class = EditBoardForm
    template_name = "edit_board.html"
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        user = self.request.user
        return reverse("profile", kwargs={"user__username":user.username})

    def get_object(self, queryset=None) -> Board:
        try:
            return self.model.objects.get(pk=self.kwargs['name'])
        except ObjectDoesNotExist:
            raise Http404

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        board = self.get_object()

        new_initial = {
            "title" : board.title,
            "is_private" : board.is_private,
            "description" : board.description,
            "cover" : board.cover,
        }

        initial.update(new_initial)
        return initial
    
class DetailBoardView(LoginRequiredMixin, DetailView):
    model = Board
    template_name = "detail_board.html"
    slug_field = "name"
    slug_url_kwarg = "name"
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
