from django.views import View
from django.views.generic.edit import CreateView, DeleteView
from django.shortcuts import render
from django.urls import reverse_lazy
from braces.views import LoginRequiredMixin
import time

from expressways.calculation.tasks import add
from expressways.core.models import OccurrenceConfiguration
from expressways.core.forms import OccurrenceConfigurationForm


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        form = OccurrenceConfigurationForm()
        configurations = OccurrenceConfiguration.objects.all()
        context = {
            'configurations': configurations,
            'form': form,
        }
        return render(request, 'core/home.html', context)


class NewOccurrenceConfiguration(LoginRequiredMixin, CreateView):
    model = OccurrenceConfiguration
    form_class = OccurrenceConfigurationForm
    success_url = reverse_lazy('core:home')


class DeleteOccurrenceConfiguration(LoginRequiredMixin, DeleteView):
    model = OccurrenceConfiguration
    success_url = reverse_lazy('core:home')


class CalculateView(LoginRequiredMixin, View):
    def post(self, request):
        pass
