from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class Home(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    redirect_field_name = "next"
    login_url = reverse_lazy("login")
