from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
from celery.result import AsyncResult
import time

from expressways.calculation.tasks import add, calculate
from expressways.calculation.models import CalculationResult
from expressways.core.models import OccurrenceConfiguration, Occurrence, SubOccurrence
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


class NewOccurrenceConfiguration(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = self.request.POST
        occurrence = Occurrence.objects.get(id=data.get('occurrence'))
        sub_occurrence = SubOccurrence.objects.get(id=data.get('sub_occurrence'))
        config_obj = OccurrenceConfiguration(
            occurrence=occurrence,
            sub_occurrence=sub_occurrence,
            lane_closures=data.get('lane_closures'),
            duration=data.get('duration'),
            flow=data.get('flow'),
            frequency=data.get('frequency')
        )
        config_obj.save()
        if 'task_id' in self.request.session:
            del self.request.session['task_id']
        return redirect(reverse_lazy('core:home'))

class DeleteOccurrenceConfiguration(LoginRequiredMixin, DeleteView):
    model = OccurrenceConfiguration
    success_url = reverse_lazy('core:home')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if 'task_id' in self.request.session:
            del self.request.session['task_id']
        return response


class CalculateView(LoginRequiredMixin, View):
    def get(self, request):
        #  clicked calculate button while logged out and then got redirected
        #  here after signing in
        return redirect(reverse('core:home'))

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
        res = AsyncResult(task_id)
        if res.failed():
            return JsonResponse({'msg': 'The Task Failed'}, status=500)

        result = get_object_or_404(CalculationResult, task_id=task_id)

        return JsonResponse({'objective_1': result.objective_1, 'objective_2': result.objective_2})


class SubOccurrenceOptionsView(LoginRequiredMixin, ListView):
    model = SubOccurrence
    template_name = 'core/sub_occurrences_list_options.html'
    context_object_name = 'sub_occurrences'

    def get_queryset(self):
        occurrence_id = self.request.GET.get('occurrence')
        query_set = self.model.objects.filter(occurrence_id=occurrence_id).order_by('name')
        return query_set
