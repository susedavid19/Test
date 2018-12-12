from django.views import View
from django.views.generic.edit import CreateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
import time

from expressways.calculation.tasks import add, calculate
from expressways.calculation.models import CalculationResult
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
        items = []
        for item in OccurrenceConfiguration.objects.all():
            items.append({
                'lane_closures': item.lane_closures,
                'duration': item.duration,
                'flow': item.flow,
                'frequency': item.frequency,
            })

        res = calculate.delay(items)

        request.session['task_id'] = res.id

        return redirect(reverse('core:home'))


class ResultView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        result = get_object_or_404(CalculationResult, task_id=task_id)

        return JsonResponse({'objective_1': result.objective_1, 'objective_2': result.objective_2})
