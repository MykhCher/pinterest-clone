from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, CreateView, DetailView, FormView, View

from pins.forms import SaveToBoard
from pins.models import Pin
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


class EditBoardView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
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
            return self.model.objects.get(title=self.kwargs['name'])
        except self.model.DoesNotExist:
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
    
    def test_func(self) -> bool:
        """Method from `UserPassesTestMixin`. Tests if user, 
        that made request is object's owner.
        """
        obj = self.get_object()
        return obj.user == self.request.user
    
class DetailBoardView(LoginRequiredMixin, DetailView):
    model = Board
    template_name = "detail_board.html"
    slug_field = "title"
    slug_url_kwarg = "board_name"
    login_url = reverse_lazy("login")
    redirect_field_name = "next"


class SaveToBoard(LoginRequiredMixin, FormView):
    form_class = SaveToBoard
    login_url = reverse_lazy("login")
    redirect_field_name = "next"
    
    def get_success_url(self) -> str:
        """Redirect back to a previous page."""
        return self.request.META.get("HTTP_REFERER")
    
    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass the instance of user, that made request, into a form."""
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs
    
    def form_valid(self, form: SaveToBoard) -> HttpResponse:
        pin = Pin.objects.get(pk=self.kwargs['pk'])
        instance = form.save(commit=False)
        instance.user = pin.user
        instance.save
        board = Board.objects.get(id=self.request.POST.get('board'))
        board.pins.add(pin)
        return super().form_valid(form)

class RemoveFromBoard(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = reverse_lazy("login")
    redirect_field_name = "next"

    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")
     
    def test_func(self) -> bool:
        """Method from `UserPassesTestMixin`. Tests if user, 
        that made request is object's owner.
        """
        try:
            obj = Board.objects.get(title=self.kwargs.get('board_name'))
        except Board.DoesNotExist:
            return Http404

        return obj.user == self.request.user
    
    def post(self, request: HttpRequest, pin_pk: int, board_name: str) -> HttpResponse:
        try:
            pin = Pin.objects.get(pk=pin_pk)
            board = Board.objects.get(title=board_name)
        except (Pin.DoesNotExist, Board.DoesNotExist):
            return Http404
        
        board.pins.remove(pin)
        return redirect(self.get_success_url())
