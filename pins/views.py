from typing import Any, Dict
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, Http404, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView

from .forms import CreatePinForm, EditPinForm, SaveToBoard, CommentForm
from .models import Pin, Comment
from boards.forms import CreateBoardForm
from boards.models import Board
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
    
    def form_valid(self, form: CreateBoardForm) -> HttpResponse:
        form.instance.user = self.request.user
        return super().form_valid(form)
    
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
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs.setdefault('user', self.request.user)
        return kwargs

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
 
class DetailPinView(LoginRequiredMixin, DetailView):
    model = Pin
    template_name = "detail_pin.html"
    redirect_field_name = "next"
    login_url = reverse_lazy("login")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        pin = self.model.objects.get(pk=self.kwargs['pk'])
        is_following = self.request.user.followers.filter(following=pin.user).first()

        new_context = {
            'pin' : pin,
            'save_to_board_form': SaveToBoard(self.request.user, instance=pin),
            'edit_form' : EditPinForm(self.request.user, instance=pin),
            'comment_form' : CommentForm(),
            'is_following' : is_following,
            'related_pins' : self.get_related_pins(self.kwargs['pk'])
        }

        context.update(new_context)

        return context
    
    def get_related_pins(self, pin_pk: int) -> set:
        related_pins = []
        boards = Board.objects.filter().all() 

        # Get all boards that contains the current pin.
        related_board = [
            board for board in boards if board.pins.filter(id=pin_pk).first()
        ] 

        # Get all pins in related boards,
        # The output may be a nested list of queryset objects.
        related_pins_lists = [board.pins.all() for board in related_board]

        # Make one list out of nested lists of pins.
        for i in range(len(related_pins_lists)):
            for p in related_pins_lists[i]:
                related_pins.append(p)

        # Remove current pin from related pins.
        for pin in related_pins:
            if pin.id == pin_pk:
                related_pins.remove(pin) 
        
        return set(related_pins)
       

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
    

class CreateCommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    redirect_field_name = "next"
    login_url = reverse_lazy("login")
    
    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")
    
    def form_valid(self, form: CommentForm) -> HttpResponse:
        comment = form.save(commit=False)
        comment.user = self.request.user
        try:
            comment.pin = Pin.objects.get(pk=self.kwargs.get("pk"))
        except self.model.DoesNotExist:
            return Http404
        comment.save()
        return super().form_valid(form)
    
class DeleteCommentView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get_success_url(self) -> str:
        return self.request.META.get("HTTP_REFERER")

    def test_func(self) -> bool:
        """Method from `UserPassesTestMixin`. Tests if user, 
        that made request is object's owner.
        """
        obj = self.get_object()
        return obj.user == self.request.user
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())
    