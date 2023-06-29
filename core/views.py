from typing import Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from pins.models import Pin


class Home(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    redirect_field_name = "next"
    login_url = reverse_lazy("login")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.setdefault('pins', Pin.objects.all())
        return context
