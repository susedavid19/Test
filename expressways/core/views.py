from django.views.generic.base import TemplateView
from braces.views import LoginRequiredMixin

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'core/home.html'
